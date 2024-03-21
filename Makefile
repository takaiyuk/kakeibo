include .env
.PHONY: run test mypy clean lambda-layer

AWS_PROFILE := $(if $(AWS_PROFILE),$(AWS_PROFILE),default)
REPOSITORY := takaiyuk/kakeibo-lambda
LAMBDA_FUNCTION_NAME := kakeibo

run:
	rye run kakeibo

test:
	rye run pytest tests --cov --cov-branch --cov-report=html

lint:
	rye fmt
	rye lint --fix
	rye run mypy src/kakeibo

docker-build:
	docker build -f ./docker/lambda/Dockerfile -t $(REPOSITORY) . --build-arg PYTHON_VERSION=$(shell cat .python-version | cut -d'.' -f1,2)

docker-push:
	aws ecr get-login-password --region ap-northeast-1 --profile $(AWS_PROFILE) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com
	docker tag $(REPOSITORY):latest $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com/$(REPOSITORY):latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com/$(REPOSITORY):latest

lambda-test:
	# curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
	docker run -p 9000:8080 -v $(PWD)/.env:/var/task/.env -v $(PWD)/client_secret.json:/var/task/client_secret.json $(REPOSITORY):latest

lambda-set-env:
	rye run invoke lambda-set-env --profile $(AWS_PROFILE) --function-name $(LAMBDA_FUNCTION_NAME)
