from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from cloud.config import (
    FIREBASE_STORAGE_USER_FOLDER,
    FIREBASE_USER_DRAWING_FIRESTORE_COLLECTION,
    FIREBASE_USER_DRAWING_STORAGE_GCODE_FILENAME,
)
from cloud.db.base import Database
from cloud.types import GCodeSettings


class Drawing(BaseModel):
    x: list[float]
    y: list[float]
    stops: list[int]
    gcode: Optional[str]
    plot: Optional[str]
    settings: Optional[GCodeSettings]

    @classmethod
    def get_by_user(cls, user_uuid: str, db: Database) -> Drawing:
        data = db.retrieve_document(
            collection=FIREBASE_USER_DRAWING_FIRESTORE_COLLECTION, document_id=user_uuid
        )
        return cls(**data)

    def save_for_user(
        self, user_uid: str, update_fields: list[str], db: Database
    ) -> None:
        if not self.gcode:
            raise ValueError("You cannot save Drawing with no gcode.")
        data_to_update = {
            key: value for key, value in dict(self).items() if key in update_fields
        }
        db.update_document(
            collection=FIREBASE_USER_DRAWING_FIRESTORE_COLLECTION,
            document_id=user_uid,
            data=data_to_update,
        )
        path = f"{FIREBASE_STORAGE_USER_FOLDER}/{user_uid}/{FIREBASE_USER_DRAWING_STORAGE_GCODE_FILENAME}"
        db.upload_file_from_str(path=path, file_content=self.gcode)
