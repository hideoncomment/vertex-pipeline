from kfp import dsl
from kfp.dsl import Artifact, Output, Input, Model
import os
import logging
from src.config import settings
from google_cloud_pipeline_components.v1.model import ModelUploadOp
from google.cloud import aiplatform

logging.info("[Definitions] Config carregada via Pydantic.")
logging.info(f"Imagem: {settings.FULL_IMAGE_URI}")

@dsl.component(
    base_image="python:3.12",
    packages_to_install=[
        "opentelemetry-api>=1.40.0",
        "opentelemetry-exporter-gcp-trace>=1.11.0",
        "opentelemetry-sdk>=1.40.0"
    ]
)
def get_tracer_id(project_id: str, output_trace: Output[Artifact]):

    from opentelemetry import trace
    from opentelemetry.propagate import extract
    from opentelemetry.propagate import inject
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    
    exporter = CloudTraceSpanExporter(project_id=project_id)
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("pipeline-treino"):
        print("Iniciando a pipeline e gerando o ID raiz...")
        
        carrier = {}
        inject(carrier)
        traceparent = carrier.get("traceparent", "")
        
        with open(output_trace.path, 'w') as f:
            f.write(traceparent)
        print(traceparent)
            
    provider.shutdown()


@dsl.container_component
def load_op(name: str, input_trace_path: Input[Artifact], input_component_name: str, output_load_dataset: Output[Artifact]):
    return dsl.ContainerSpec(
        image=settings.FULL_IMAGE_URI, 
        command=["python", "-m", "src.components.load"], 
        args=[
            "--name", name,
            "--input-trace-path", input_trace_path.path,
            "--input-component-name", input_component_name,
            "--output-load-dataset", output_load_dataset.path
        ]
    )

@dsl.container_component
def preprocess_op(name: str, input_load_dataset: Input[Artifact], input_trace_path: Input[Artifact], input_component_name: str, output_preprocess_dataset: Output[Artifact]):
    return dsl.ContainerSpec(
        image=settings.FULL_IMAGE_URI, 
        command=["python", "-m", "src.components.preprocess_train"], 
        args=[
            "--name", name,
            "--input-load-file", input_load_dataset.path,
            "--input-trace-path", input_trace_path.path,
            "--input-component-name", input_component_name,
            "--output-preprocess-file", output_preprocess_dataset.path
        ]
    )

@dsl.container_component
def training_op(name: str, input_preprocess_dataset: Input[Artifact], input_trace_path: Input[Artifact], input_component_name: str, output_training_model: Output[Artifact]):
    return dsl.ContainerSpec(
        image=settings.FULL_IMAGE_URI, 
        command=["python", "-m", "src.components.train"], 
        args=[
            "--name", name,
            "--input-preprocess-dataset", input_preprocess_dataset.path,
            "--input-trace-path", input_trace_path.path,
            "--input-component-name", input_component_name,
            "--output-training-model", output_training_model.path,
        ]
    )

@dsl.container_component
def save_model_op(name: str, input_trace_path: Input[Artifact], input_component_name: str, output_training_model: Input[Artifact]):
    return dsl.ContainerSpec(
        image=settings.FULL_IMAGE_URI, 
        command=["python", "-m", "src.components.save_model"], 
        args=[
            "--name", name,
            "--project", settings.GCP_PROJECT_ID,
            "--location", settings.GCP_REGION,
            "--image", settings.FULL_IMAGE_URI,
            "--input-training-model", output_training_model.path,
            "--input-trace-path", input_trace_path.path,
            "--input-component-name", input_component_name
        ]
    )

# --- PIPELINE ---
@dsl.pipeline(
    name="training-pipeline",
    description="Pipeline de treinamento",
    pipeline_root=settings.GCP_BUCKET
)
def training_pipeline(
    name: str = "Developer",
):
    get_tracer_id_task = (
        get_tracer_id(
            project_id=settings.GCP_PROJECT_ID
        ) #type: ignore
    )

    load_task = (
        load_op(
            name=name,
            input_trace_path=get_tracer_id_task.outputs["output_trace"],
            input_component_name = "load-op"
        )
        .set_cpu_limit("1")
        .set_memory_limit("4G")
    )

    preprocess_task = (
        preprocess_op(
            name=name,
            input_load_dataset=load_task.outputs["output_load_dataset"],
            input_trace_path=get_tracer_id_task.outputs["output_trace"],
            input_component_name = "preprocess-op"
        )
        .set_cpu_limit("1")
        .set_memory_limit("4G")
    )

    model_training_task = (
        training_op(
            name=name,
            input_preprocess_dataset=preprocess_task.outputs["output_preprocess_dataset"],
            input_trace_path=get_tracer_id_task.outputs["output_trace"],
            input_component_name = "training-op"
        )
    )

    model_upload_task = (
        save_model_op(
            name=name,
            output_training_model=model_training_task.outputs["output_training_model"],
            input_trace_path=get_tracer_id_task.outputs["output_trace"],
            input_component_name = "save-model-op"
        )
    )