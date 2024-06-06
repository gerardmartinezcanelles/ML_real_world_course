build:
	docker build -t trade-producer .

run: build
	docker run -it --network=redpanda_network trade-producer