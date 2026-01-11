terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.22" # Versão estável mais atual
    }
  }

  backend "gcs" {
    bucket  = "alexsyk-terraform-state" # Nome único global do bucket
    prefix  = "terraform/state/teste"            # Caminho dentro do bucket
  }

}

provider "google" {
  project = "vertex-pipeline-484002"
  region  = "us-central1"
}