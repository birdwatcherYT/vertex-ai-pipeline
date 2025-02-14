from kfp.dsl import component, Output, Dataset


def create_preprocess_component(base_image: str):
    @component(base_image=base_image)
    def preprocess(data: str, output_data: Output[Dataset]):
        """データを前処理するコンポーネント"""
        with open(output_data.path, "w") as f:
            f.write(f"Processed: {data}")

    return preprocess
