import argparse


def train(project_id, input_path, run_id, output_path):
    """モデルを学習するコンポーネント"""
    with open(input_path, "r") as f:
        data = f.read()

    with open(output_path, "w") as f:
        f.write(f"Trained model with {data}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", type=str, required=True)
    parser.add_argument("--input_path", type=str, required=True)
    parser.add_argument("--run_id", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    args = parser.parse_args()

    train(args.project_id, args.input_path, args.run_id, args.output_path)
