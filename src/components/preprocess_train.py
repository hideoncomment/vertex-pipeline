import argparse
import pandas as pd
import os
import logging
from src.utils.step import BaseStep
import numpy as np

class PreprocessStep(BaseStep):

    def get_parser(self):
        p = super().get_parser()
        p.add_argument("--name", type=str)
        p.add_argument("--input-load-file", type=str)
        p.add_argument("--input-trace-path", type=str)
        p.add_argument("--output-preprocess-file", type=str)
        return p

    def main(self, args):
        logging.info("--- [PREPROCESS] Limpando dados ---")
        df = pd.read_parquet(args.input_load_file)
        df['feature_limpa'] = df['valor'] * 2 # Exemplo de transformação
        X_teste = np.array([[45], [55], [70], [90], [110], [130], [150]])

        df_teste = pd.DataFrame(X_teste, columns=['tamanho_m2'])
        df_teste.to_parquet(args.output_preprocess_file, index=False)
        logging.info("--- [PREPROCESS] Dados limpos com sucesso ---")

if __name__ == "__main__":
    PreprocessStep().run()