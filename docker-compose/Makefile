start-redpanda:
	docker compose -f redpanda.yml up -d

stop-redpanda:
	docker compose -f redpanda.yml down

build-feature-pipeline:
	docker compose -f feature_pipeline.yml build

run-feature-pipeline: build-feature-pipeline
	docker compose -f feature_pipeline.yml up -d

stop-feature-pipeline:
	docker compose -f feature_pipeline.yml down