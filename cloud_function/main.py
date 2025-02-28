import argparse
import os

from flask import Request
from google.cloud import aiplatform

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")


# Cloud Functionsで呼ぶ
def handle_http(request: Request):
    params = request.get_json() if request.is_json else {}

    job = aiplatform.PipelineJob(
        project=PROJECT_ID,
        location=REGION,
        display_name="vertex-ai-pipeline",
        template_path="vertex_ai_pipeline.json",
        pipeline_root=f"gs://{PROJECT_ID}-vertex-pipelines",
        parameter_values={
            "project_id": PROJECT_ID,
            "data": params["data"],
        },
    )
    job.submit(
        service_account=f"vertex-pipelines-sa@{PROJECT_ID}.iam.gserviceaccount.com"
    )

    return "OK"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--request-body", default="{}")
    args = parser.parse_args()
    body = args.request_body

    req = Request.from_values(
        method="POST",
        content_type="application/json",
        content_length=len(body),
        data=body,
    )
    handle_http(req)
