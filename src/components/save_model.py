import argparse
import pandas as pd
import logging
from src.utils.step import BaseStep
from google.cloud import aiplatform

class SaveModel(BaseStep):

    def get_parser(self):
        p = super().get_parser()
        p.add_argument("--name", type=str)
        p.add_argument("--project", type=str)
        p.add_argument("--location", type=str)
        p.add_argument("--image", type=str)
        p.add_argument("--input-training-model", type=str)
        p.add_argument("--input-trace-path", type=str)
        p.add_argument("--input-component-name", type=str)
        return p

    def main(self, args):
        aiplatform.init(project=args.project, location=args.location)
        models = aiplatform.Model.list(filter=f'display_name="{args.name}"')
        
        parent_arg = None

        if models:
            parent_arg = models[0].resource_name
        else:
            print("New Model")

        model = aiplatform.Model.upload(
            display_name = args.name,
            artifact_uri = args.input_training_model,
            parent_model=parent_arg,
            serving_container_image_uri=args.image
        )

if __name__ == "__main__":
    SaveModel().run()