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
	docker build -f ./docker/lambda/Dockerfile -t kakeibo . --build-arg PYTHON_VERSION=$(cat .python-version | cut -d'.' -f1,2)
