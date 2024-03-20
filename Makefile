include .env
.PHONY: run test mypy clean lambda-layer

run:
	rye run kakeibo

test:
	rye run pytest tests --cov --cov-branch --cov-report=html

lint:
	rye fmt
	rye lint --fix
	rye run mypy src/kakeibo

docker-build:
	docker build -f ./docker/lambda/Dockerfile -t takaiyuk/kakeibo-lambda . --build-arg PYTHON_VERSION=$(cat .python-version | cut -d'.' -f1,2)

docker-push:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com
	make docker-build
	docker tag takaiyuk/kakeibo-lambda:latest $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com/takaiyuk/kakeibo-lambda:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com/takaiyuk/kakeibo-lambda:latest
