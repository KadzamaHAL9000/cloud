from __future__ import annotations

import subprocess

import pytest
from fastapi.testclient import TestClient

from cloud.config import OPENSCAD_EXECUTABLE_PATH
from cloud.main import app

client = TestClient(app)


@pytest.mark.smoke
def test_index_page_should_return_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Welcome to Chocolate Fiesta Cloud"


@pytest.mark.smoke
def test_openscad_executable_should_exist():
    assert OPENSCAD_EXECUTABLE_PATH
    subprocess.run(
        [
            OPENSCAD_EXECUTABLE_PATH,
            "--version",
        ],
        check=True,
    )
