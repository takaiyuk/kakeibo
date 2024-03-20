include .env
.PHONY: run test mypy clean lambda-layer

REPOSITORY := takaiyuk/kakeibo-lambda

run:
	rye run kakeibo

test:
	rye run pytest tests --cov --cov-branch --cov-report=html

lint:
	rye fmt
	rye lint --fix
	rye run mypy src/kakeibo

docker-build:
	docker build -f ./docker/lambda/Dockerfile -t $(REPOSITORY) . --build-arg PYTHON_VERSION=$(cat .python-version | cut -d'.' -f1,2)

docker-push:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com
	make docker-build
	docker tag $(REPOSITORY):latest $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com/$(REPOSITORY):latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com/$(REPOSITORY):latest

lambda-set-env:
	rye run invoke lambda-set-env
