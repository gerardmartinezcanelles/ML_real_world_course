build:
	docker build -t trade_to_ohlc .

run: build
	docker run -it --network=redpanda_network \
	--env KAFKA_INPUT_TOPIC=trade \
	--env KAFKA_OUTPUT_TOPIC=ohlc \
	--env KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
	--env OHCL_WINDOW_SECONDS=10 \
	trade_to_ohlc 

lint:
	ruff check --fix

format:
	ruff format .