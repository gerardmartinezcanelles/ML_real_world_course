run-dev:
	poetry run python src/main.py

build:
	docker build -t kafka_to_feature_store .

run: build
	docker run -it --network=redpanda_network \
	--env HOPSWORKS_API_KEY=et248JpHv46nfHEF.5JtXmYckY9wliw16gDAaydtYfVwP43bTiqQTTxhZxsyW0YAY6iGEAt6SdW8jn1Jz \
	--env HOPSWORKS_PROJECT_NAME=gerardma \
	--env KAFKA_TOPIC=ohlc \
	--env KAKFA_BROKER_ADDRESS=redpanda-0:9092 \
	--env FEATURE_GROUP_NAME=ohlc_feature_group \
	--env FEATURE_GROUP_VERSION=1 \
	kafka_to_feature_store 

lint:
	poetry run ruff check --fix

format:
	poetry run ruff format .

lint-and-format: lint format