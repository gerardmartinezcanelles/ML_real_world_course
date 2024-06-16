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

run-backfill-pipeline: build-feature-pipeline
	docker compose -f backfill_pipeline.yml up -d

stop-backfill-pipeline: 	
	docker compose -f backfill_pipeline.yml down