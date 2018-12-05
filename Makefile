WORK_DIR = $(shell pwd)
OWNER = feature
REPOSITORY = 685249416972.dkr.ecr.ap-south-1.amazonaws.com/$(OWNER)
APP_NAME = address-service
GLOBAL_VERSION = latest
BASE_VERSION = base
GIT = $(shell which git)
BUILD = $(WORK_DIR)
DOCKER := $(shell which docker)
VIRTUAL_ENV_DIR = ${CONDA_PREFIX}
PYTHON = $(VIRTUAL_ENV_DIR)/bin/python
FLAKE = $(shell which flake8)
PYTEST = $(shell which pytest)
ifeq ($(APP_VERSION),)
	APP_VERSION = $(shell $(GIT) describe --abbrev=0 2>/dev/null)
endif
TAG_VERSION = $(REPOSITORY)/$(APP_NAME):$(APP_VERSION)
BASE_TAG = $(REPOSITORY)/$(APP_NAME):$(BASE_VERSION)-$(APP_VERSION)
BASE_GLOBAL = $(REPOSITORY)/$(APP_NAME):$(BASE_VERSION)-$(GLOBAL_VERSION)
TAG_GLOBAL = $(REPOSITORY)/$(APP_NAME):$(GLOBAL_VERSION)
DEPLOYMENT_DIR = $(WORK_DIR)/deployment/
COPY = $(shell which cp)

clean:
	if [ -d $(DEPLOYMENT_DIR) ]; then\
		rm -rvf $(DEPLOYMENT_DIR);\
	fi
	rm -rvf latest.tar

check_lint:
	$(FLAKE) ./

test_integration: check_lint
	$(PYTEST)

build_tar: clean
	$(GIT) archive -o latest.tar $(APP_VERSION)

prepare_base: clean
	mkdir $(DEPLOYMENT_DIR)
	$(COPY) requirements.txt $(DEPLOYMENT_DIR)
	$(COPY) Dockerfile.base $(DEPLOYMENT_DIR)Dockerfile

prepare_build: build_tar
	mkdir $(DEPLOYMENT_DIR)
	$(COPY) $(BUILD)/latest.tar $(DEPLOYMENT_DIR)
	$(COPY) Dockerfile $(DEPLOYMENT_DIR)


build_base: prepare_base
	$(DOCKER) build --build-arg BASE_VERSION=$(BASE_VERSION)-$(APP_VERSION) -t $(BASE_TAG) -t $(BASE_GLOBAL) $(DEPLOYMENT_DIR)

build_docker: prepare_build
	$(DOCKER) pull $(BASE_GLOBAL)
	$(DOCKER) tag $(BASE_GLOBAL) $(APP_NAME):$(BASE_VERSION)-$(GLOBAL_VERSION)
	$(DOCKER) build --build-arg APP_VERSION=$(APP_VERSION) -t $(TAG_VERSION) -t $(TAG_GLOBAL) $(DEPLOYMENT_DIR)

run_docker:
	$(DOCKER) run -d -p 8080:8080 --env-file env $(TAG_GLOBAL)

push_base: build_base
	$(DOCKER) push $(BASE_TAG)
	$(DOCKER) push $(BASE_GLOBAL)

push_docker: build_docker
	$(DOCKER) push $(TAG_VERSION)
	$(DOCKER) push $(TAG_GLOBAL)
