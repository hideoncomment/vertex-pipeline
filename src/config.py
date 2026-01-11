from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    GCP_PROJECT_ID: str = "vertex-pipeline-484002"
    GCP_REGION: str = "us-central1"
    GCP_BUCKET: str = "gs://opentelemetry-dev/"
    PIPELINE_NAME: str = "opentelemtry"
    FULL_IMAGE_URI: str = "us-central1-docker.pkg.dev/vertex-pipeline-484002/opentelemetry/debug-img:latest"
    BUILD_ID: str = "teste"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()