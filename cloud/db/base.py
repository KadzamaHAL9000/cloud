from abc import ABC


class Database(ABC):
    def retrieve_document(self, collection: str, document_id: str) -> dict:
        ...

    def create_document(self, collection: str, document_id: str, data: dict) -> None:
        ...

    def update_document(self, collection: str, document_id: str, data: dict) -> None:
        ...

    def upload_file_from_str(self, path: str, file_content: str) -> None:
        ...

    def upload_file_from_filename(self, path: str, file_name: str) -> None:
        ...

    def file_exists(self, path: str) -> bool:
        ...

    def get_file_public_url(self, path: str) -> str:
        ...
