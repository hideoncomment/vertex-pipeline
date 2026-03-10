import argparse
import pandas as pd
import os
import logging
from src.utils.step import BaseStep

class LoadStep(BaseStep):

    def get_parser(self):
        p = super().get_parser()
        p.add_argument("--name")
        p.add_argument("--output-load-dataset", type=str)
        p.add_argument("--input-trace-path", type=str)
        p.add_argument("--input-component-name", type=str)
        return p

    def main(self, args):

        logging.info("="*40)
        logging.info(f"--- [LOAD] Carregando dados do Projeto {args.name} ---")
        logging.info(f"Salvando os dados em {args.output_load_dataset}")

        df = pd.DataFrame({'id': range(10), 'valor': [x * 1.5 for x in range(10)]})
        
        df.to_parquet(args.output_load_dataset, index=False)
        
        logging.info("✅ Processo finalizado com sucesso.")
        logging.info("="*40)

if __name__ == "__main__":
    LoadStep().run()