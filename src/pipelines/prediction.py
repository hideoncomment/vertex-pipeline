from kfp import dsl
from kfp.dsl import Artifact, Output, Input, Dataset
import os
import logging
from src.config import settings

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
    
    with tracer.start_as_current_span("pipeline-predict"):
        print("Iniciando a pipeline e gerando o ID raiz...")
        
        carrier = {}
        inject(carrier)
        traceparent = carrier.get("traceparent", "")
        
        with open(output_trace.path, 'w') as f:
            f.write(traceparent)
        print(traceparent)
            
    provider.shutdown()

@dsl.component(base_image="python:3.11-slim")
def generate_offsets(total_rows: int, chunk_size: int) -> list:
    return [i for i in range(0, total_rows, chunk_size)]

@dsl.component(packages_to_install=["google-cloud-aiplatform"], base_image="python:3.12-slim")
def import_model_resource_name(
        display_name: str, 
        project: str, 
        location: str, 
        model_artifact: Output[Artifact]
    ):
    from google.cloud import aiplatform
    
    aiplatform.init(project=project, location=location)
    
    print(f"Buscando modelo: {display_name}")
    models = aiplatform.Model.list(filter=f'display_name="{display_name}"')
    
    if not models:
        raise ValueError(f"❌ Erro: Modelo '{display_name}' não encontrado.")
    
    found_id = models[0].resource_name
    model_artifact.uri = f"https://{location}-aiplatform.googleapis.com/v1/{found_id}"
    model_artifact.metadata["ResourceName"] = found_id
    print(f"✅ ID encontrado: {found_id}")

@dsl.container_component
def load_op(name: str, input_trace_path: Input[Artifact], input_component_name: str, output_load_dataset: Output[Dataset]):
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
        command=["python", "-m", "src.components.preprocess_predict"], 
        args=[
            "--name", name,
            "--input-load-file", input_load_dataset.path,
            "--input-trace-path", input_trace_path.path,
            "--input-component-name", input_component_name,
            "--output-preprocess-dataset", output_preprocess_dataset.path
        ]
    )

@dsl.container_component
def predict_op(name: str, input_preprocess_dataset: Input[Artifact], input_predict_model: Input[Artifact], input_trace_path: Input[Artifact], input_component_name: str, output_prediction_results: Output[Artifact]):
    return dsl.ContainerSpec(
        image=settings.FULL_IMAGE_URI, 
        command=["python", "-m", "src.components.predict"], 
        args=[
            "--name", name,
            "--input-preprocess-dataset", input_preprocess_dataset.path,
            "--input-predict-model", input_predict_model.path,
            "--input-trace-path", input_trace_path.path,
            "--input-component-name", input_component_name,
            "--output-prediction-results", output_prediction_results.path
        ]
    )

@dsl.container_component
def save_results_op(name: str, input_prediction_results_dataset: Input[Artifact], input_trace_path: Input[Artifact], input_component_name: str):
    return dsl.ContainerSpec(
        image=settings.FULL_IMAGE_URI, 
        command=["python", "-m", "src.components.save_results"], 
        args=[
            "--name", name,
            "--input-prediction-results-dataset", input_prediction_results_dataset.path,
            "--input-trace-path", input_trace_path.path,
            "--input-component-name", input_component_name
        ]
    )

# --- PIPELINE ---
@dsl.pipeline(
    name="prediction-pipeline",
    description="Pipeline simples para teste"
)
def prediction_pipeline(
    name: str = "Developer"
):
    
    get_tracer_id_task = (
        get_tracer_id(
            project_id="vertex-pipeline-484002"
        ) #type: ignore
    )

    get_id_task = import_model_resource_name(
        display_name=name,
        project=settings.GCP_PROJECT_ID,
        location=settings.GCP_REGION
    ) # type: ignore

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

    prediction_task = (
        predict_op(
            name=name,
            input_preprocess_dataset=preprocess_task.outputs["output_preprocess_dataset"],
            input_predict_model=get_id_task.outputs["model_artifact"],
            input_trace_path=get_tracer_id_task.outputs["output_trace"],
            input_component_name = "predict-op"
        )
        .set_cpu_limit("1")
        .set_memory_limit("4G")
    )