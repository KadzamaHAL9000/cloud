import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from cloud.db.base import Database
from cloud.main import app
from cloud.services.stl import STLGeneratorService
from cloud.types import OpenSCADModelSettings

client = TestClient(app)


@pytest.fixture()
def dummy_db(mocker):
    return mocker.MagicMock(spec=Database)


@pytest.mark.smoke
def test_openscad_endpoint_should_return_stl_url():
    response = client.post("/api/stl-generator/")

    assert response.status_code == 201
    assert "url" in response.json()


@pytest.mark.slow
def test_openscad_should_render_stl(dummy_db):
    settings = OpenSCADModelSettings()
    settings.text = uuid4().hex[:5]
    renderer = STLGeneratorService(settings, db=dummy_db)
    renderer._create_temp_files()

    assert not os.path.getsize(renderer.stl_file.name)
    try:
        renderer._subprocess_run_render()
        assert os.path.getsize(renderer.stl_file.name)
    finally:
        renderer._cleanup_temp_files()
