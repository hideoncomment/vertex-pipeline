import yaml
import logging
import os
from google.cloud import aiplatform
from kfp import compiler
import src.pipelines.prediction as defs_p
import src.pipelines.training as defs_t
from src.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def submit(type):
    logging.info(f"--- Iniciando Scheduler ---")

    project_id = settings.GCP_PROJECT_ID
    region = settings.GCP_REGION
    bucket = settings.GCP_BUCKET
    pipeline_name = settings.PIPELINE_NAME
    build_id = settings.BUILD_ID

    logging.info(f"Alvo: {project_id} | Pipeline: {pipeline_name}")

    aiplatform.init(
        project=project_id,
        location=region,
        staging_bucket=bucket
    )

    json_file = f"{pipeline_name}-{type}-{build_id}.json"

    if type == "training":
        compiler.Compiler().compile(
            pipeline_func = defs_t.training_pipeline, # type: ignore
            package_path=json_file
        )
    elif type == "prediction":
        compiler.Compiler().compile(
            pipeline_func = defs_p.prediction_pipeline, # type: ignore
            package_path=json_file
        )
    else:
        return 1

    display_name = f"{pipeline_name}-{type}-{build_id}"

    logging.info(f"Enviando a pipeline no Vetex AI")

    pipeline_job = aiplatform.PipelineJob(
        display_name=display_name,
        template_path=json_file,
        parameter_values={"name": pipeline_name},
        enable_caching=False
    )

    pipeline_job_schedule = aiplatform.PipelineJobSchedule(
        pipeline_job=pipeline_job,
        display_name=display_name
    )

    schedules = aiplatform.PipelineJobSchedule.list(
        filter=f"display_name={display_name}"
    )

    if not schedules:
        pipeline_job_schedule.create(
            cron="0 0 1 1 *",
            max_concurrent_run_count=1,
            max_run_count=None,
        )
    else:
        existing_schedule = schedules[0]
        existing_schedule.delete()
        pipeline_job_schedule.create(
            cron="0 0 1 2 *",
            max_concurrent_run_count=1,
            max_run_count=None,
        )

    logging.info(f"Pipeline Schedule criado com sucesso!")