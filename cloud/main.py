from __future__ import annotations

from typing import Iterator

from fastapi import Depends, FastAPI, status
from fastapi.responses import Response

from cloud import middleware
from cloud.db.base import Database
from cloud.db.firebase import Firebase
from cloud.services.drawing import UserDrawingService
from cloud.services.stl import STLGeneratorService
from cloud.types import GCodeSettings, OpenSCADModelSettings

app = FastAPI()
middleware.add_sentry_middleware(app)
middleware.add_cors_middleware(app)


def get_db() -> Iterator[Database]:
    yield Firebase()


@app.post("/api/user/{user_uid}/drawing/", status_code=status.HTTP_201_CREATED)
async def user_drawing_plot(
    user_uid: str,
    settings: GCodeSettings = None,
    db: Database = Depends(get_db),
) -> str | Response:
    try:
        settings = settings or GCodeSettings()
        drawing_service = UserDrawingService(user_uid, settings, db)
        plot = drawing_service()
        return plot
    except FileNotFoundError:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/api/stl-generator/", status_code=status.HTTP_201_CREATED)
async def stl_generator(
    settings: OpenSCADModelSettings = None,
    db: Database = Depends(get_db),
) -> dict:
    settings = settings or OpenSCADModelSettings()
    stl_generator = STLGeneratorService(settings, db)
    stl_url = await stl_generator()
    return {"url": stl_url}


@app.get("/")
async def index() -> str:
    return "Welcome to Chocolate Fiesta Cloud"
