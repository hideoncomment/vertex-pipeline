import argparse
import pandas as pd
import logging
from src.utils.step import BaseStep
from sklearn.linear_model import LinearRegression
import numpy as np
import joblib
import os

class TrainModel(BaseStep):

    def get_parser(self):
        p = super().get_parser()
        p.add_argument("--name", type=str)
        p.add_argument("--input-preprocess-dataset", type=str)
        p.add_argument("--input-trace-path", type=str)
        p.add_argument("--output-training-model", type=str)
        return p

    def main(self, args):
        
        X = np.array([[40], [50], [60], [80], [100], [120]]) 
        y = np.array([150000, 200000, 250000, 320000, 400000, 480000])
        df = pd.read_parquet(args.input_preprocess_dataset)
        
        modelo = LinearRegression()
        
        modelo.fit(X, y)
        os.makedirs(args.output_training_model, exist_ok=True)
        joblib.dump(modelo, os.path.join(args.output_training_model, "model.joblib"))

if __name__ == "__main__":
    TrainModel().run()