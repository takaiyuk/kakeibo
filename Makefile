include .env
.PHONY: run test mypy clean lambda-layer

AWS_PROFILE := $(if $(AWS_PROFILE),$(AWS_PROFILE),default)
REPOSITORY := takaiyuk/kakeibo-lambda
LAMBDA_FUNCTION_NAME := kakeibo

run:
	uv run kakeibo

test:
	uv run pytest tests --cov --cov-branch --cov-report=html

lint:
	uv run ruff format
	uv run ruff check --fix
	uv run mypy src/kakeibo

docker-build:
	docker build -f ./docker/lambda/Dockerfile -t $(REPOSITORY) . --build-arg PYTHON_VERSION=3.12

docker-push:
	aws ecr get-login-password --region ap-northeast-1 --profile $(AWS_PROFILE) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com
	docker tag $(REPOSITORY):latest $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com/$(REPOSITORY):latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com/$(REPOSITORY):latest

lambda-test:
	# curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
	docker run -p 9000:8080 -v $(PWD)/.env:/var/task/.env -v $(PWD)/client_secret.json:/var/task/client_secret.json $(REPOSITORY):latest

lambda-set-env:
	uv run invoke lambda-set-env --profile $(AWS_PROFILE) --function-name $(LAMBDA_FUNCTION_NAME)

echo-env:
	@echo "AWS_PROFILE: $(AWS_PROFILE)"
	@echo "AWS_ACCOUNT_ID: $(AWS_ACCOUNT_ID)"
	@echo "REPOSITORY: $(REPOSITORY)"
	@echo "LAMBDA_FUNCTION_NAME: $(LAMBDA_FUNCTION_NAME)"
