from kfp import compiler
from kfp.dsl import component, pipeline, Output, Dataset, Model, Input
from .component.preprocess import create_preprocess_component
from .component.train import create_train_component


def build_pipeline(image):
    preprocess_component = create_preprocess_component(image)
    train_component = create_train_component(image)

    @pipeline(
        name="vertex-ai-pipeline",
        description="シンプルな Vertex AI パイプライン",
    )
    def vertex_ai_pipeline(data: str):
        preprocessed_data = preprocess_component(data=data)
        trained_model = train_component(training_data=preprocessed_data.output)

        # キャッシュを無効に
        preprocessed_data.set_caching_options(False)
        trained_model.set_caching_options(False)

    compiler.Compiler().compile(
        pipeline_func=vertex_ai_pipeline,
        package_path="vertex_ai_pipeline.json",
    )
