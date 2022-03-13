.PHONY: run test mypy clean lambda-layer

run:
	python -m kakeibo

test:
	pytest --cov --cov-branch --cov-report=html kakeibo

mypy:
	mypy kakeibo

clean:
	./scripts/clean_caches.sh

lambda-layer:
	./scripts/clean_caches.sh \
	&& mkdir python \
	&& pip install -t python requests \
	&& zip -r9 layer.zip python \
	&& rm -r python
