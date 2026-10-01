# Variables
IMAGE_NAME ?= fedora-j2-processor
IMAGE_TAG ?= latest
DATA_DIR ?= $(shell pwd)/templates
DATA_DIR_AGENT ?= $(shell pwd)/agent
CONTAINER_TOOL ?= podman

.PHONY: help build run test clean

help: ## Show available commands
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?##/ {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the Podman container image using Containerfile
	$(CONTAINER_TOOL) build -f Containerfile -t $(IMAGE_NAME):$(IMAGE_TAG) .

run: ## Run template processing on DATA_DIR (e.g., make run DATA_DIR=/path/to/j2/files)
	@mkdir -p $(DATA_DIR)
	$(CONTAINER_TOOL) run --rm \
		-v $(DATA_DIR):/data:Z \
		$(IMAGE_NAME):$(IMAGE_TAG)

run_agent: ## Run template processing on DATA_DIR (e.g., make run DATA_DIR=/path/to/j2/files)
	@mkdir -p $(DATA_DIR_AGENT)
	$(CONTAINER_TOOL) run --rm \
		-v $(DATA_DIR_AGENT):/data:Z \
		$(IMAGE_NAME):$(IMAGE_TAG)


clean: ## Remove built image and clean up local test output directory
	-$(CONTAINER_TOOL) rmi $(IMAGE_NAME):$(IMAGE_TAG)
	rm -rf test_data
