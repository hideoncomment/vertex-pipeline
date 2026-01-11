import argparse
import pandas as pd
import logging
from src.utils.step import BaseStep

class SaveResults(BaseStep):

    def get_parser(self):
        p = super().get_parser()
        p.add_argument("--name", type=str)
        p.add_argument("--input-prediction-results-dataset", type=str)
        p.add_argument("--input-trace-path", type=str)
        return p

    def main(self, args):
        df = pd.read_parquet(args.input_prediction_results_dataset)
        logging.info(f"--- [SAVE] Salvando {len(df)} linhas em {args.input_prediction_results_dataset} ---")
        logging.info(df.head())

if __name__ == "__main__":
    SaveResults().run()