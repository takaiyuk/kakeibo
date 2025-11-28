# https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/python-image.html
ARG PYTHON_VERSION=3.13
ARG UV_VERSION=0.9.13
FROM ghcr.io/astral-sh/uv:${UV_VERSION}-python${PYTHON_VERSION}-trixie-slim AS source
FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}

WORKDIR ${LAMBDA_TASK_ROOT}

COPY --from=source /usr/local/bin/uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=README.md,target=README.md \
    uv build --wheel
RUN pip install dist/kakeibo-0.1.0-py3-none-any.whl \
    && rm -rf dist build __pypackages__ .uv /usr/local/bin/uv

COPY src/kakeibo ${LAMBDA_TASK_ROOT}/kakeibo

CMD [ "kakeibo.lambda.lambda_handler" ]
