import argparse
import subprocess
import time
from pathlib import Path

import boto3


def terraform_output(name: str) -> str:
    result = subprocess.run(
        ["terraform", "output", "-raw", name],
        cwd="terraform/environments/dev",
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def start_query(client, database: str, workgroup: str, query: str) -> str:
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": database},
        WorkGroup=workgroup,
    )
    return response["QueryExecutionId"]


def wait_for_query(client, query_id: str) -> None:
    while True:
        response = client.get_query_execution(QueryExecutionId=query_id)
        state = response["QueryExecution"]["Status"]["State"]

        if state == "SUCCEEDED":
            return

        if state in {"FAILED", "CANCELLED"}:
            reason = response["QueryExecution"]["Status"].get("StateChangeReason", "Unknown")
            raise RuntimeError(f"Athena query {query_id} ended with {state}: {reason}")

        print(f"Waiting for query {query_id}: {state}")
        time.sleep(2)


def empty_s3_prefix(bucket: str, prefix: str) -> None:
    s3 = boto3.resource("s3")
    bucket_resource = s3.Bucket(bucket)
    bucket_resource.objects.filter(Prefix=prefix).delete()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create curated user experiment facts table.")
    parser.add_argument(
        "--sql-path",
        type=Path,
        default=Path("sql/create_user_experiment_facts.sql"),
    )
    args = parser.parse_args()

    database = terraform_output("glue_database_name")
    workgroup = terraform_output("athena_workgroup_name")
    curated_bucket = terraform_output("curated_bucket_name")

    curated_location = f"s3://{curated_bucket}/tables/user_experiment_facts/"
    curated_prefix = "tables/user_experiment_facts/"

    client = boto3.client("athena")

    drop_query = "DROP TABLE IF EXISTS user_experiment_facts"
    create_query = args.sql_path.read_text().replace("${CURATED_LOCATION}", curated_location)

    print("Dropping existing user_experiment_facts table...")
    drop_id = start_query(client, database, workgroup, drop_query)
    wait_for_query(client, drop_id)

    print("Cleaning curated table output prefix...")
    empty_s3_prefix(curated_bucket, curated_prefix)

    print("Creating curated user_experiment_facts table...")
    create_id = start_query(client, database, workgroup, create_query)
    wait_for_query(client, create_id)

    print("Created user_experiment_facts")
    print(f"Location: {curated_location}")


if __name__ == "__main__":
    main()
