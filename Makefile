# Export requirements dependencies to prod environment
export_requirements:
	uv export --format requirements.txt --no-hashes --no-emit-project > requirements.txt

build_debug:
	sudo docker buildx build --platform linux/amd64 -t us-central1-docker.pkg.dev/vertex-pipeline-484002/opentelemetry/debug-img:latest .

push_debug:
	sudo docker push us-central1-docker.pkg.dev/vertex-pipeline-484002/opentelemetry/debug-img:latest

run_train:
	python main.py --launcher --type training

schedule_train:
	python main.py --scheduler --type training

run_predict:
	python main.py --launcher --type prediction

schedule_predict:
	python main.py --scheduler --type prediction