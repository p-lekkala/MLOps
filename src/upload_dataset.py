import json
import os
import sys
from argparse import ArgumentParser

from azureml.core import Dataset, Workspace
from azureml.data.dataset_factory import DataType


def parse_args(argv):
    ap = ArgumentParser("upload_dataset")

    ap.add_argument("--subscription_id", required=True)
    ap.add_argument("--resource_group", required=True)
    ap.add_argument("--workspace_name", required=True)
    ap.add_argument("--dataset_directory_name", default="data")
    ap.add_argument("--dataset_file_name", default="cardiovascular-disease.csv")
    ap.add_argument("--dataset_name", default="cardiovascular_disease_train_dataset")
    ap.add_argument(
        "--dataset_description",
        default="70,000 records of patients' data relating to cardiovascular disease collected at the moment of medical examination",
    )
    ap.add_argument(
        "--dataset_tags", type=json.loads, default={"project": "deployment-template"}
    )
    args, _ = ap.parse_known_args(argv)

    return args


def main():
    # Parse command line arguments
    args = parse_args(sys.argv[1:])

    # Retreive workspace
    workspace = Workspace.get(
        subscription_id=args.subscription_id,
        resource_group=args.resource_group,
        name=args.workspace_name,
    )

    # Retreive datastore
    datastore = workspace.get_default_datastore()

    # Upload the local file from src_dir to the target_path in datastore
    datastore.upload(
        src_dir=args.dataset_directory_name, target_path=args.dataset_directory_name
    )

    # Create a dataset referencing the cloud location
    dataset = Dataset.Tabular.from_delimited_files(
        datastore.path(
            os.path.join(args.dataset_directory_name, args.dataset_file_name)
        ),
        set_column_types={
            "age": DataType.to_float(),
            "gender": DataType.to_string(),
            "height": DataType.to_float(),
            "weight": DataType.to_float(),
            "systolic": DataType.to_float(),
            "diastolic": DataType.to_float(),
            "cholesterol": DataType.to_string(),
            "glucose": DataType.to_string(),
            "smoker": DataType.to_string(),
            "alcoholic": DataType.to_string(),
            "active": DataType.to_string(),
            "cardiovascular_disease": DataType.to_string(),
        },
    )

    # Assign timestamp column for Tabular Dataset to activate Time Series related APIs
    dataset = dataset.with_timestamp_columns(timestamp="datetime")

    # Register dataset to Workspace
    dataset.register(
        workspace,
        args.dataset_name,
        create_new_version=True,
        description=args.dataset_description,
        tags=args.dataset_tags,
    )

    print("Dataset registered")


if __name__ == "__main__":
    main()
