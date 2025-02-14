from kfp.dsl import component, Output, Dataset, Input, Model


def create_train_component(base_image: str):
    @component(base_image=base_image)
    def train(training_data: Input[Dataset], model: Output[Model]):
        """モデルを学習するコンポーネント"""
        with open(training_data.path, "r") as f:
            data = f.read()

        with open(model.path, "w") as f:
            f.write(f"Trained model with {data}")

    return train
