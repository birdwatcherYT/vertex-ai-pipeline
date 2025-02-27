from kfp import compiler
from kfp.dsl import (
    pipeline,
    Output,
    Input,
    Artifact,
    ContainerSpec,
    container_component,
    PIPELINE_JOB_RESOURCE_NAME_PLACEHOLDER,
)


def build_pipeline(image: str):
    @container_component
    def preprocess_component(
        project_id: str,
        dataset_path: str,
        output_data: Output[Artifact],
        run_id: str = PIPELINE_JOB_RESOURCE_NAME_PLACEHOLDER,
    ):
        return ContainerSpec(
            image=image,
            command=[
                "uv",
                "run",
                "python",
                "-m",
                "src.component.preprocess",
            ],
            args=[
                f"--project_id={project_id}",
                f"--run_id={run_id}",
                f"--dataset_path={dataset_path}",
                f"--output_path={output_data.path}",
            ],
        )

    @container_component
    def train_component(
        project_id: str,
        input_data: Input[Artifact],
        output_data: Output[Artifact],
        run_id: str = PIPELINE_JOB_RESOURCE_NAME_PLACEHOLDER,
    ):

        return ContainerSpec(
            image=image,
            command=[
                "uv",
                "run",
                "python",
                "-m",
                "src.component.train",
            ],
            args=[
                f"--project_id={project_id}",
                f"--run_id={run_id}",
                f"--input_path={input_data.path}",
                f"--output_path={output_data.path}",
            ],
        )

    @pipeline(name="vertex-ai-pipeline")
    def vertex_ai_pipeline(project_id: str, data: str):
        preprocessed_data = preprocess_component(
            project_id=project_id,
            dataset_path=data,
        )
        trained_model = train_component(
            project_id=project_id,
            input_data=preprocessed_data.outputs["output_data"],
        )
        # trained_model.after(preprocessed_data)

        # キャッシュを無効に
        preprocessed_data.set_caching_options(False)
        trained_model.set_caching_options(False)

    compiler.Compiler().compile(
        pipeline_func=vertex_ai_pipeline,
        package_path="vertex_ai_pipeline.json",
    )
