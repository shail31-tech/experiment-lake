import math
import subprocess
import time

import boto3
import pandas as pd
import streamlit as st
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportions_ztest

st.set_page_config(page_title="ExperimentLake", layout="wide")


def terraform_output(name: str) -> str:
    result = subprocess.run(
        ["terraform", "output", "-raw", name],
        cwd="terraform/environments/dev",
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


@st.cache_data(ttl=300)
def run_athena_query(query: str) -> pd.DataFrame:
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

        time.sleep(1)

    results = client.get_query_results(QueryExecutionId=query_id)
    rows = results["ResultSet"]["Rows"]

    values = [[cell.get("VarCharValue", "") for cell in row["Data"]] for row in rows]
    header = values[0]
    data = values[1:]

    return pd.DataFrame(data, columns=header)


def load_variant_summary() -> pd.DataFrame:
    query = """
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

    df = run_athena_query(query)

    for column in ["users", "activations", "subscriptions", "revenue"]:
        df[column] = pd.to_numeric(df[column])

    df["activation_rate"] = df["activations"] / df["users"]
    df["subscription_rate"] = df["subscriptions"] / df["users"]
    df["avg_revenue_per_user"] = df["revenue"] / df["users"]

    return df


def load_segment_summary(segment_column: str) -> pd.DataFrame:
    allowed_segments = {"device_type", "traffic_source", "plan_type", "country"}
    if segment_column not in allowed_segments:
        raise ValueError(f"Unsupported segment column: {segment_column}")

    query = f"""
    SELECT
        {segment_column} AS segment,
        variant,
        count(*) AS users,
        sum(did_activate) AS activations,
        round(sum(revenue), 2) AS revenue
    FROM user_experiment_facts
    GROUP BY
        {segment_column},
        variant
    ORDER BY
        {segment_column},
        variant
    """

    df = run_athena_query(query)

    for column in ["users", "activations", "revenue"]:
        df[column] = pd.to_numeric(df[column])

    df["activation_rate"] = df["activations"] / df["users"]
    df["avg_revenue_per_user"] = df["revenue"] / df["users"]

    return df


def compare_to_control(df: pd.DataFrame) -> pd.DataFrame:
    control = df[df["variant"] == "control"].iloc[0]
    rows = []

    for _, row in df.iterrows():
        if row["variant"] == "control":
            continue

        count = [row["activations"], control["activations"]]
        nobs = [row["users"], control["users"]]
        _, p_value = proportions_ztest(count=count, nobs=nobs)

        absolute_lift = row["activation_rate"] - control["activation_rate"]
        relative_lift = absolute_lift / control["activation_rate"]

        pooled_rate = (row["activations"] + control["activations"]) / (
            row["users"] + control["users"]
        )
        standard_error = math.sqrt(
            pooled_rate
            * (1 - pooled_rate)
            * ((1 / row["users"]) + (1 / control["users"]))
        )

        rows.append(
            {
                "variant": row["variant"],
                "activation_rate": row["activation_rate"],
                "absolute_lift": absolute_lift,
                "relative_lift": relative_lift,
                "p_value": p_value,
                "ci_lower": absolute_lift - 1.96 * standard_error,
                "ci_upper": absolute_lift + 1.96 * standard_error,
                "decision": "Ship" if p_value < 0.05 and absolute_lift > 0 else "Do not ship",
            }
        )

    return pd.DataFrame(rows)


def segment_lift_vs_control(segment_df: pd.DataFrame) -> pd.DataFrame:
    control_df = segment_df[segment_df["variant"] == "control"][
        ["segment", "activation_rate"]
    ].rename(columns={"activation_rate": "control_activation_rate"})

    comparison_df = segment_df[segment_df["variant"] != "control"].merge(
        control_df,
        on="segment",
        how="left",
    )

    comparison_df["absolute_lift"] = (
        comparison_df["activation_rate"] - comparison_df["control_activation_rate"]
    )
    comparison_df["relative_lift"] = (
        comparison_df["absolute_lift"] / comparison_df["control_activation_rate"]
    )

    return comparison_df.sort_values(
        ["relative_lift", "users"],
        ascending=[False, False],
    )


def sample_ratio_status(df: pd.DataFrame) -> tuple[float, str]:
    observed = df["users"].tolist()
    expected = [sum(observed) / len(observed)] * len(observed)
    _, p_value, _, _ = chi2_contingency([observed, expected])

    status = "Pass" if p_value >= 0.01 else "Investigate"
    return p_value, status


st.title("ExperimentLake")
st.caption("Serverless A/B testing analytics platform")

summary = load_variant_summary()
comparisons = compare_to_control(summary)
srm_p_value, srm_status = sample_ratio_status(summary)

ship_candidates = comparisons[comparisons["decision"] == "Ship"]
if not ship_candidates.empty:
    winner = ship_candidates.sort_values("absolute_lift", ascending=False).iloc[0]
else:
    winner = comparisons.sort_values("absolute_lift", ascending=False).iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Users", f"{summary['users'].sum():,.0f}")
col2.metric("Best Variant", winner["variant"])
col3.metric("Best Lift", f"{winner['relative_lift']:.1%}")
col4.metric("Sample Ratio", srm_status)

st.subheader("Variant Summary")

display_summary = summary.copy()
display_summary["activation_rate"] = display_summary["activation_rate"].map("{:.2%}".format)
display_summary["subscription_rate"] = display_summary["subscription_rate"].map("{:.2%}".format)
display_summary["avg_revenue_per_user"] = display_summary["avg_revenue_per_user"].map(
    "${:.2f}".format
)
display_summary["revenue"] = display_summary["revenue"].map("${:,.2f}".format)

st.dataframe(display_summary, use_container_width=True, hide_index=True)

st.subheader("Control Comparisons")

display_comparisons = comparisons.copy()
for column in ["activation_rate", "absolute_lift", "relative_lift", "ci_lower", "ci_upper"]:
    display_comparisons[column] = display_comparisons[column].map("{:.2%}".format)

display_comparisons["p_value"] = display_comparisons["p_value"].map("{:.6f}".format)

st.dataframe(display_comparisons, use_container_width=True, hide_index=True)

st.subheader("Activation Rate by Variant")

chart_df = summary.set_index("variant")[["activation_rate"]]
st.bar_chart(chart_df)

st.subheader("Segment Analysis")

segment_column = st.selectbox(
    "Segment",
    options=["device_type", "traffic_source", "plan_type", "country"],
    index=0,
)

segment_summary = load_segment_summary(segment_column)
segment_comparisons = segment_lift_vs_control(segment_summary)

segment_chart = segment_summary.pivot(
    index="segment",
    columns="variant",
    values="activation_rate",
).sort_index()
st.bar_chart(segment_chart)

display_segment_comparisons = segment_comparisons[
    [
        "segment",
        "variant",
        "users",
        "activation_rate",
        "control_activation_rate",
        "absolute_lift",
        "relative_lift",
        "avg_revenue_per_user",
    ]
].copy()

for column in [
    "activation_rate",
    "control_activation_rate",
    "absolute_lift",
    "relative_lift",
]:
    display_segment_comparisons[column] = display_segment_comparisons[column].map(
        "{:.2%}".format
    )

display_segment_comparisons["avg_revenue_per_user"] = display_segment_comparisons[
    "avg_revenue_per_user"
].map("${:.2f}".format)

st.dataframe(display_segment_comparisons, use_container_width=True, hide_index=True)

st.subheader("Decision")

if srm_status != "Pass":
    st.warning(
        f"Sample ratio mismatch check failed or needs investigation. p-value: {srm_p_value:.6f}"
    )
else:
    st.success(f"Sample ratio check passed. p-value: {srm_p_value:.6f}")

for _, row in comparisons.iterrows():
    if row["decision"] == "Ship":
        st.success(
            f"{row['variant']} shows statistically significant positive lift "
            f"({row['relative_lift']:.1%}, p={row['p_value']:.6f})."
        )
    else:
        st.error(
            f"{row['variant']} does not show enough evidence to ship "
            f"(p={row['p_value']:.6f})."
        )
