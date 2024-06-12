run-dev:
	poetry run python src/main.py

build:
	docker build -t kafka_to_feature_store .

run: build
	docker run -it --network=redpanda_network \
	--env KAKFA_BROKER_ADDRESS=redpanda-0:9092 \
	--env-file .env \
	kafka_to_feature_store 

lint:
	poetry run ruff check --fix

format:
	poetry run ruff format .

lint-and-format: lint format