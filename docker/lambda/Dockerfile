# https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/python-image.html
ARG PYTHON_VERSION
FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}

RUN dnf update -y \
    && dnf install -y gzip

WORKDIR ${LAMBDA_TASK_ROOT}

ENV RYE_HOME /home/.rye
ENV PATH ${RYE_HOME}/shims:${PATH}
RUN curl -sSf https://rye.astral.sh/get | RYE_NO_AUTO_INSTALL=1 RYE_INSTALL_OPTION="--yes" bash

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=requirements.lock,target=requirements.lock \
    --mount=type=bind,source=requirements-dev.lock,target=requirements-dev.lock \
    --mount=type=bind,source=.python-version,target=.python-version \
    --mount=type=bind,source=README.md,target=README.md \
    rye build --wheel --clean --quiet
RUN pip install dist/kakeibo-0.1.0-py3-none-any.whl

COPY src/kakeibo ${LAMBDA_TASK_ROOT}/kakeibo

CMD [ "kakeibo.lambda.lambda_handler" ]
