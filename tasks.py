import os
import subprocess
import invoke

from google.cloud import aiplatform, storage
from pathlib import Path
import datetime

ROOT_DIR = Path(__file__).parent


@invoke.task
def docker_build(c, prod: bool = False):
    """Dockerビルド（--prodオプションでprod向け）"""
    image = c.config.prod.image if prod else c.config.dev.image
    subprocess.run(
        f"docker build --tag {image} .",
        cwd=ROOT_DIR,
        shell=True,
        check=True,
    )


@invoke.task
def docker_run(c, prod: bool = False):
    """Docker起動"""
    image = c.config.prod.image if prod else c.config.dev.image
    credentials = "-v ~/.config/gcloud:/root/.config/gcloud"
    subprocess.run(
        f"docker run -p {c.config.port}:{c.config.port} --rm -it {credentials} {image}",
        cwd=ROOT_DIR,
        shell=True,
        check=True,
    )


@invoke.task
def docker_push(c, prod: bool = False):
    """DockerをArtifact Registry/Container Registryへpush（--prodオプションでprod向け）"""
    image = c.config.prod.image if prod else c.config.dev.image
    dt_now = datetime.datetime.now()
    tag = dt_now.strftime("%Y%m%d%H%M%S")
    subprocess.run(
        f'docker image tag "{image}:latest" "{image}:{tag}"',
        cwd=ROOT_DIR,
        shell=True,
        check=True,
    )
    subprocess.run(
        f'docker push "{image}:latest"',
        cwd=ROOT_DIR,
        shell=True,
        check=True,
    )
    subprocess.run(
        f'docker push "{image}:{tag}"',
        cwd=ROOT_DIR,
        shell=True,
        check=True,
    )


@invoke.task
def cloud_build(c, prod: bool = False):
    project = c.config.prod.project if prod else c.config.dev.project
    image = c.config.prod.image if prod else c.config.dev.image
    dt_now = datetime.datetime.now()
    tag = dt_now.strftime("%Y%m%d%H%M%S")
    sa = f"projects/{project}/serviceAccounts/cloud-build-sa@{project}.iam.gserviceaccount.com"
    subprocess.run(
        f"gcloud builds submit --config cloudbuild.yaml --service-account={sa} --project={project} --async --substitutions=_IMAGE={image},_TAG={tag}",
        cwd=ROOT_DIR,
        shell=True,
        check=True,
    )


@invoke.task
def build_pipeline(c, prod: bool = False):
    project = c.config.prod.project if prod else c.config.dev.project
    aiplatform.init(project=project, location=c.config.region)
    image = c.config.prod.image if prod else c.config.dev.image
    from pipeline import build_pipeline

    build_pipeline(image)


@invoke.task
def run_pipeline(c, prod: bool = False):
    project = c.config.prod.project if prod else c.config.dev.project
    aiplatform.init(project=project, location=c.config.region)

    job = aiplatform.PipelineJob(
        display_name="vertex-ai-pipeline",
        template_path="vertex_ai_pipeline.json",
        pipeline_root=f"gs://{project}-vertex-pipelines",
        parameter_values={"project_id": project, "data": "sample input data"},
    )
    job.submit(service_account=f"vertex-pipelines-sa@{project}.iam.gserviceaccount.com")
