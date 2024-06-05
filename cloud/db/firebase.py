from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore, storage

from cloud.config import FIREBASE_CONFIG, FIREBASE_CREDENTIALS
from cloud.db.base import Database

credential = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(credential=credential, options=FIREBASE_CONFIG)
firebase_client = firestore.client()
firebase_bucket = storage.bucket()


class Firebase(Database):
    def __init__(self) -> None:
        super().__init__()

    def retrieve_document(self, collection: str, document_id: str) -> dict:
        data = (
            firebase_client.collection(collection).document(document_id).get().to_dict()
        )
        if not data:
            raise FileNotFoundError
        return data

    def create_document(
        self, collection: str, document_id: str, data: dict, **kwargs: Any
    ) -> None:
        firebase_client.collection(collection).document(document_id).set(data, **kwargs)

    def update_document(self, collection: str, document_id: str, data: dict) -> None:
        self.create_document(
            collection=collection, document_id=document_id, data=data, merge=True
        )

    def upload_file_from_str(self, path: str, file_content: str) -> None:
        blob = firebase_bucket.blob(path)
        blob.upload_from_string(file_content, content_type="application/octet-stream")

    def upload_file_from_filename(self, path: str, file_name: str) -> None:
        blob = firebase_bucket.blob(path)
        blob.upload_from_filename(file_name, content_type="application/octet-stream")

    def file_exists(self, path: str) -> bool:
        return firebase_bucket.blob(path).exists()

    def get_file_public_url(self, path: str) -> str:
        blob = firebase_bucket.blob(path)
        blob.make_public()
        return blob.public_url
