![Header](/assets/kubeflow_banner.png)

# Proof of Concept - Kubeflow SDK with Opentelemetry
This project aims to automatize the process of creating and scheduling pipelines on Google Cloud Vertex AI Pipelines monitoring the traces using OpenTelemetry.

# Architecture

![Architecture](/assets/Vertex%20AI%20Script%20Export-2026-03-09-225511.png)

The architecture diagram illustrates the end-to-end telemetry flow. The local Python environment utilizes the Kubeflow SDK to compile and submit the machine learning pipeline. The OpenTelemetry Python SDK is instrumented to capture this process, generating spans for the pipeline's lifecycle. As the pipeline executes on Google Cloud Vertex AI, the tracing data is exported via the OTel Exporter directly to Google Cloud Trace, providing a centralized view of the operations.

# Prerequisites

- uv
- gcloud application json

# How to Run

## Configure your environment

- pip install uv
- uv venv
- uv sync
  
## Build and Test

You can simply run `make run_train` or `make run_predict` to launch a pipeline on Vertex, or if you want to schedule just run the command `make run_schedule_train` or `make run_schedule_predict`.

# Results / Trace Output

![Architecture](/assets/Vertex%20AI%20Training%20Tracer.png)
![Architecture](/assets/Vertex%20AI%20Predict%20Tracer.png)

The screenshots above show the successful capture of distributed traces in Google Cloud Trace.

Training Trace: Displays the span hierarchy and execution duration for the model training workflow initiated by the run_train command.

Predict Trace: Highlights the telemetry data for the inference phase (run_predict), tracking the latency of the prediction jobs.

These results validate that the OpenTelemetry context is correctly propagated from the Kubeflow SDK down to the observability backend, accurately mapping the pipeline steps.

# GSoC Relevance

This Proof of Concept (PoC) was developed to validate the core mechanics of OpenTelemetry integration within a Kubeflow-based environment. By successfully instrumenting a pipeline execution on Vertex AI and exporting the distributed traces to Google Cloud Trace, this project demonstrates a practical understanding of:

OpenTelemetry API/SDK configuration in Python.

Span creation and context propagation across machine learning workflows.

Telemetry exporter setup and integration with cloud-based observability backends.

For the GSoC 2026 project, this tracing logic and vendor-neutral instrumentation pattern will be pushed down into the source code of the Kubeflow SDK itself. The technical foundation validated in this PoC will be directly applied to natively instrument SDK components such as the PipelinesClient, TrainerClient, OptimizerClient, and ModelRegistryClient. The ultimate goal is to provide out-of-the-box observability for all Kubeflow users, allowing them to collect metrics and distributed traces without writing custom telemetry code.