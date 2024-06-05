style:
	poetry run mypy .
	poetry run flake8 .

test:
	poetry run pytest

run:
	poetry run uvicorn cloud.main:app --reload

install:
	poetry install

activate:
	poetry shell
