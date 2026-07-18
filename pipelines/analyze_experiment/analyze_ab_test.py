import math
import subprocess
import time

import boto3
import pandas as pd
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportions_ztest


def terraform_output(name: str) -> str:
    result = subprocess.run(
        ["terraform", "output", "-raw", name],
        cwd="terraform/environments/dev",
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def run_athena_query(query: str) -> list[list[str]]:
    database = terraform_output("glue_database_name")
    workgroup = terraform_output("athena_workgroup_name")

    client = boto3.client("athena")
    query_id = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": database},
        WorkGroup=workgroup,
    )["QueryExecutionId"]

    while True:
        execution = client.get_query_execution(QueryExecutionId=query_id)
        state = execution["QueryExecution"]["Status"]["State"]

        if state == "SUCCEEDED":
            break

        if state in {"FAILED", "CANCELLED"}:
            reason = execution["QueryExecution"]["Status"].get("StateChangeReason", "Unknown")
            raise RuntimeError(f"Athena query failed: {reason}")

        time.sleep(2)

    results = client.get_query_results(QueryExecutionId=query_id)
    rows = results["ResultSet"]["Rows"]

    return [
        [cell.get("VarCharValue", "") for cell in row["Data"]]
        for row in rows
    ]


def query_summary() -> pd.DataFrame:
    rows = run_athena_query(
        """
        SELECT
            variant,
            count(*) AS users,
            sum(did_activate) AS activations,
            sum(did_subscribe) AS subscriptions,
            round(sum(revenue), 2) AS revenue
        FROM user_experiment_facts
        GROUP BY variant
        ORDER BY variant
        """
    )

    header = rows[0]
    data = rows[1:]

    df = pd.DataFrame(data, columns=header)
    numeric_columns = ["users", "activations", "subscriptions", "revenue"]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column])

    df["activation_rate"] = df["activations"] / df["users"]
    df["subscription_rate"] = df["subscriptions"] / df["users"]
    df["avg_revenue_per_user"] = df["revenue"] / df["users"]

    return df


def compare_to_control(df: pd.DataFrame) -> pd.DataFrame:
    control = df[df["variant"] == "control"].iloc[0]
    rows = []

    for _, variant_row in df.iterrows():
        variant = variant_row["variant"]

        if variant == "control":
            continue

        count = [variant_row["activations"], control["activations"]]
        nobs = [variant_row["users"], control["users"]]

        _, p_value = proportions_ztest(count=count, nobs=nobs)

        control_rate = control["activation_rate"]
        variant_rate = variant_row["activation_rate"]
        absolute_lift = variant_rate - control_rate
        relative_lift = absolute_lift / control_rate

        pooled_rate = (variant_row["activations"] + control["activations"]) / (
            variant_row["users"] + control["users"]
        )
        standard_error = math.sqrt(
            pooled_rate
            * (1 - pooled_rate)
            * ((1 / variant_row["users"]) + (1 / control["users"]))
        )

        ci_lower = absolute_lift - 1.96 * standard_error
        ci_upper = absolute_lift + 1.96 * standard_error

        rows.append(
            {
                "variant": variant,
                "control_rate": control_rate,
                "variant_rate": variant_rate,
                "absolute_lift": absolute_lift,
                "relative_lift": relative_lift,
                "p_value": p_value,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "decision": "ship" if p_value < 0.05 and absolute_lift > 0 else "do_not_ship",
            }
        )

    return pd.DataFrame(rows)


def sample_ratio_check(df: pd.DataFrame) -> tuple[float, str]:
    observed = df["users"].tolist()
    expected = [sum(observed) / len(observed)] * len(observed)

    _, p_value, _, _ = chi2_contingency([observed, expected])

    status = "pass" if p_value >= 0.01 else "investigate_sample_ratio_mismatch"
    return p_value, status


def main() -> None:
    summary = query_summary()
    comparisons = compare_to_control(summary)
    srm_p_value, srm_status = sample_ratio_check(summary)

    print("\nVariant Summary")
    print(summary.to_string(index=False))

    print("\nControl Comparisons")
    print(comparisons.to_string(index=False))

    print("\nSample Ratio Check")
    print(f"p_value={srm_p_value:.6f}")
    print(f"status={srm_status}")


if __name__ == "__main__":
    main()
