import argparse
import pandas as pd
import logging
from src.utils.step import BaseStep
from google.cloud import aiplatform

class PredictStep(BaseStep):

    def get_parser(self):
        p = super().get_parser()
        p.add_argument("--name", type=str)
        p.add_argument("--input-preprocess-dataset", type=str)
        p.add_argument("--input-predict-model", type=str)
        p.add_argument("--input-trace-path", type=str)
        p.add_argument("--offset")
        p.add_argument("--output-prediction-results", type=str)
        return p

    def main(self, args):
        logging.info(f"{args.name}")
        # df = pd.read_parquet(args.input_preprocess_dataset)
        # df['prediction_score'] = 0.95

        # df.to_parquet(args.output_prediction_results) # Salva sem adicionar extensão extra, pois o path já é completo
        
        # criar o sql
        logging.info(f"lendo tabela do {args.input_preprocess_dataset}")

        logging.info("Arquivo salvo com sucesso.")

if __name__ == "__main__":
    PredictStep().run()