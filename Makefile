# Makefile for managing the Quay API Docker project

IMAGE_NAME = quay-api
CONTAINER_NAME = quay-api
TAG = latest

.PHONY: build run stop remove logs clean

# Build the Docker image
build:
	docker build -t $(IMAGE_NAME):$(TAG) .


# Run the container
run:
	docker run --name $(CONTAINER_NAME) -d $(IMAGE_NAME):$(TAG)

# Run the app locally using venv and Uvicorn
run-local:
	source venv/bin/activate && uvicorn src.main:app --host 0.0.0.0 --port 8000

# Stop the running container
stop:
	docker stop $(CONTAINER_NAME) || true

# Remove the container
remove:
	docker rm $(CONTAINER_NAME) || true

# Show logs
logs:
	docker logs -f $(CONTAINER_NAME)

# Clean up image and container
clean: stop remove
	docker rmi $(IMAGE_NAME):$(TAG) || true

# Rebuild everything from scratch
rebuild: clean build run
