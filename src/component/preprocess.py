import argparse


def preprocess(project_id: str, data: str, run_id: str, output_path: str):
    """データを前処理するコンポーネント"""
    with open(output_path, "w") as f:
        f.write("preprocess\n")
        f.write(f"project_id: {project_id}\n")
        f.write(f"data: {data}\n")
        f.write(f"run_id: {run_id}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", type=str, required=True)
    parser.add_argument("--data", type=str, required=True)
    parser.add_argument("--run_id", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    args = parser.parse_args()

    preprocess(args.project_id, args.data, args.run_id, args.output_path)
