FROM python:3.9

WORKDIR /app

# Install OpenSCAD
RUN apt-get update -y && \ 
    apt-get install -y openscad && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry install --no-root --no-dev

# Install fonts
COPY ./cloud/static/fonts /usr/share/fonts/truetype

COPY ./ /app

CMD ["uvicorn", "cloud.main:app", "--host", "0.0.0.0", "--port", "5000"]
