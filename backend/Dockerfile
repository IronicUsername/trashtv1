FROM sidestream/python-poetry:3.9 as dependency-base

# copy and install dependencies to make sure they are cached
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev

# 3. Copy over production code for runtime
FROM dependency-base as production

COPY ./src /app/
WORKDIR /app

# Service hostname
ENV HOST=0.0.0.0

CMD ["poetry", "run", "poe", "start"]
