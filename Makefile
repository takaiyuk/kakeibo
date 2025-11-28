include .env
.PHONY: run lint test test-ci docker-build docker-push lambda-test lambda-set-env echo-env

AWS_PROFILE := $(if $(AWS_PROFILE),$(AWS_PROFILE),default)
REPOSITORY := takaiyuk/kakeibo-lambda
LAMBDA_FUNCTION_NAME := kakeibo
LAMBDA_FUNCTION_TIMEOUT_SECONDS := 10

run:
	uv run kakeibo

lint:
	uv run ruff format
	uv run ruff check --fix
	uv run mypy src/kakeibo

test:
	uv run pytest tests --cov --cov-branch --cov-report=html

test-ci:
	uv run pytest tests --cov=src --cov-report=term-missing --junitxml=pytest.xml | tee pytest-coverage.txt

docker-build:
	docker build -f ./docker/lambda/Dockerfile -t $(REPOSITORY) . --build-arg PYTHON_VERSION=$(shell grep -E '^requires-python' pyproject.toml | sed 's/.*">= \([0-9.]*\)".*/\1/') --build-arg UV_VERSION=$(shell uv --version | cut -d' ' -f2)

docker-push:
	aws ecr get-login-password --region ap-northeast-1 --profile $(AWS_PROFILE) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com
	docker tag $(REPOSITORY):latest $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com/$(REPOSITORY):latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com/$(REPOSITORY):latest

lambda-test:
	# curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
	docker run -p 9000:8080 -v $(PWD)/.env:/var/task/.env -v $(PWD)/client_secret.json:/var/task/client_secret.json -e AWS_LAMBDA_FUNCTION_TIMEOUT=$(LAMBDA_FUNCTION_TIMEOUT_SECONDS) $(REPOSITORY):latest

lambda-set-env:
	uv run invoke lambda-set-env --profile $(AWS_PROFILE) --function-name $(LAMBDA_FUNCTION_NAME)

echo-env:
	@echo "AWS_PROFILE: $(AWS_PROFILE)"
	@echo "AWS_ACCOUNT_ID: $(AWS_ACCOUNT_ID)"
	@echo "REPOSITORY: $(REPOSITORY)"
	@echo "LAMBDA_FUNCTION_NAME: $(LAMBDA_FUNCTION_NAME)"
