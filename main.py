import argparse
import os
import sys
import logging
from pydantic_settings import BaseSettings

def start(args):

    try:
        if args.launcher:
            from src.deployment import launcher
            launcher.submit(args.type)
        elif args.scheduler:
            from src.deployment import scheduler
            scheduler.submit(args.type)
    except Exception as e:
        logging.error(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scheduler", action="store_true")
    parser.add_argument("--launcher", action="store_true")
    parser.add_argument("--type", type=str, choices=["training", "prediction"])
    args = parser.parse_args()
    start(args)