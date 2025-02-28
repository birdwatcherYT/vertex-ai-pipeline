import os
import subprocess
import invoke
import json
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

    build_pipeline(image, c.config.pipeline_json)


@invoke.task
def run_pipeline(c, prod: bool = False):
    project = c.config.prod.project if prod else c.config.dev.project

    # job = aiplatform.PipelineJob(
    #     project=project,
    #     location=c.config.region,
    #     display_name="vertex-ai-pipeline",
    #     template_path=c.config.pipeline_json,
    #     pipeline_root=f"gs://{project}-vertex-pipelines",
    #     parameter_values={"project_id": project, "data": "sample input data"},
    # )
    # job.submit(service_account=f"vertex-pipelines-sa@{project}.iam.gserviceaccount.com")

    params = {"data": "sample input data"}
    subprocess.run(
        f"""
        PROJECT_ID={project} \
        REGION={c.config.region} \
        uv run python main.py --request-body='{json.dumps(params)}'
        """,
        cwd=ROOT_DIR / "cloud_function",
        shell=True,
        check=True,
    )


@invoke.task
def run_pipeline_via_cloud_function(c, prod: bool = False):
    project = c.config.prod.project if prod else c.config.dev.project

    params = {"data": "sample input data"}
    subprocess.run(
        f"""
        curl -X POST \
            -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
            -H "Content-Type: application/json" \
            -d '{json.dumps(params)}' \
            https://us-central1-{project}.cloudfunctions.net/pipeline-run
        """,
        cwd=ROOT_DIR,
        shell=True,
        check=True,
    )


@invoke.task
def deploy_pipeline(c, prod: bool = False):
    """cloud functionにデプロイする"""
    project = c.config.prod.project if prod else c.config.dev.project
    build_sa = f"projects/{project}/serviceAccounts/cloud-build-sa@{project}.iam.gserviceaccount.com"
    run_sa = f"vertex-pipelines-sa@{project}.iam.gserviceaccount.com"

    subprocess.run(
        f"""
        gcloud functions deploy pipeline-run \
        --project {project} \
        --runtime python311 \
        --trigger-http \
        --entry-point=handle_http \
        --source=./cloud_function/ \
        --service-account={run_sa} \
        --build-service-account={build_sa} \
        --memory 512MB \
        --set-env-vars PROJECT_ID={project},REGION={c.config.region}
        """,
        cwd=ROOT_DIR,
        shell=True,
        check=True,
    )
