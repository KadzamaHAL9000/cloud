import asyncio
import hashlib
import os
import subprocess
from collections import OrderedDict
from tempfile import NamedTemporaryFile

from loguru import logger
from solid import linear_extrude, offset, resize, scad_render, square, text, translate

from cloud.config import FIREBASE_STORAGE_STL_GENERATOR_FOLDER, OPENSCAD_EXECUTABLE_PATH
from cloud.db.base import Database
from cloud.types import OpenSCADModelSettings


class STLGeneratorService:
    def __init__(self, settings: OpenSCADModelSettings, db: Database):
        self.settings = settings
        self.scad_code = self.get_scad_code()
        self.storage_path = self.get_stl_storage_path()
        self.db = db

    async def __call__(self) -> str:
        return await self.get_stl_url()

    async def get_stl_url(self) -> str:
        if self.db.file_exists(self.storage_path):
            logger.info(
                f"Cached STL found for at {self.storage_path} {self.settings.dict()}"
            )
            return self.db.get_file_public_url(self.storage_path)
        return await self.render_stl()

    async def render_stl(self) -> str:
        logger.info(
            f"Generating STL at {self.storage_path} with settings {self.settings.dict()}"
        )
        self._create_temp_files()
        try:
            await self.run_render()
            self.db.upload_file_from_filename(self.storage_path, self.stl_file.name)
            return self.db.get_file_public_url(self.storage_path)
        finally:
            self._cleanup_temp_files()

    def _create_temp_files(self) -> None:
        self.scad_file = NamedTemporaryFile(
            "w", encoding="utf-8", suffix=".scad", delete=False
        )
        self.scad_file.write(self.scad_code)
        self.scad_file.close()
        self.stl_file = NamedTemporaryFile(suffix=".stl", delete=False)
        self.stl_file.close()

    def _cleanup_temp_files(self) -> None:
        os.unlink(self.scad_file.name)
        os.unlink(self.stl_file.name)

    async def run_render(self) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: self._subprocess_run_render(),
        )

    def _subprocess_run_render(self) -> None:
        subprocess.run(
            [
                OPENSCAD_EXECUTABLE_PATH,
                "-o",
                self.stl_file.name,
                self.scad_file.name,
            ],
            check=True,
        )

    def get_stl_storage_path(self) -> str:
        settings_hash = hashlib.md5(
            str(OrderedDict(self.settings.dict())).encode()
        ).hexdigest()
        filename = f"{self.settings.text.replace(' ', '_')}.stl"
        return f"{FIREBASE_STORAGE_STL_GENERATOR_FOLDER}/{settings_hash}/{filename}"

    def get_scad_code(self) -> str:
        text_shape = resize(
            (self.settings.width, 0, self.settings.depth),
            auto=(False, True, False),
        )(
            text(
                self.settings.text,
                font=self.settings.font,
                size=self.settings.width,
                spacing=self.settings.text_spacing,
            )
        )

        shape = linear_extrude(self.settings.depth)(text_shape)
        shape += linear_extrude(self.settings.foundation_depth)(
            offset(r=self.settings.foundation_offset)(text_shape)
        )
        if " " in self.settings.text and self.settings.foundation_joiner_height > 0:
            shape += linear_extrude(self.settings.foundation_depth)(
                translate((self.settings.width * 0.05, 0.0, 0.0))(
                    resize(
                        (
                            self.settings.width * 0.95,
                            self.settings.foundation_joiner_height,
                            self.settings.depth,
                        )
                    )(square([10, 10]))
                )
            )
        return scad_render(shape)
