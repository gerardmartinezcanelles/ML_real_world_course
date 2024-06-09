FROM python:3.10.3-slim-buster

# strea output to console
ENV PYTHONUNBUFFERED=1

#install poetry inside the container
RUN pip install poetry

WORKDIR /app

# Copy or code to the docker container
COPY . /app

# install Python dependencies from the pyproject.toml file
RUN poetry install

# Entrypoint
CMD ["poetry","run","python","src/main.py"]