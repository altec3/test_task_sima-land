FROM python:3.11-slim as base_image

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.5.1

WORKDIR /tmp

RUN pip install "poetry==$POETRY_VERSION"

COPY ./poetry.lock ./pyproject.toml ./

RUN poetry export -f requirements.txt -o requirements.txt && \
    rm poetry.lock pyproject.toml && \
    pip uninstall poetry -y

WORKDIR /app

# Copy app files
COPY app .
COPY deploy/config_temp.yaml config/.
COPY entrypoint.sh .


EXPOSE 8080


FROM base_image as image

RUN pip install -r /tmp/requirements.txt && \
    pip install envsubst

ENTRYPOINT ["bash", "./entrypoint.sh"]