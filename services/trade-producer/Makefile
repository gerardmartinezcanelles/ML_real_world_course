build:
	docker build -t trade-producer .

run: build
	docker run -it --network=redpanda_network \
	--env KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
	trade-producer 


## I can just use make run and it will run both