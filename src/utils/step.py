import os
import argparse
from abc import ABC, abstractmethod
import logging
import sys
from opentelemetry import trace
from opentelemetry.propagate import extract
from opentelemetry.propagate import inject
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

class BaseStep(ABC):
    
    def run(self):

        exporter = CloudTraceSpanExporter(project_id="vertex-pipeline-484002")
        provider = TracerProvider()
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        
        tracer = trace.get_tracer(__name__)

        parser = self.get_parser()
        args = parser.parse_args()

        for key, value in vars(args).items():
            if "output" in key and isinstance(value, str) and "/gcs/" in value:
                os.makedirs(os.path.dirname(value), exist_ok=True)
                print(f"Pasta garantida para: {key}")

        with open(args.input_trace_path, 'r') as f:
            traceparent_string = f.read().strip()
        
        carrier = {"traceparent": traceparent_string}
        ctx = extract(carrier)
        print(f"--- TRACEPARENT RECEBIDO: '{traceparent_string}' ---")

        with tracer.start_as_current_span(args.input_component_name, context=ctx): #type: ignore
            print("Rodando script empacotado no container...")
            
            self.main(args)

        provider.shutdown()

    def get_parser(self):
        return argparse.ArgumentParser()
    
    @abstractmethod
    def main(self, args):
        pass