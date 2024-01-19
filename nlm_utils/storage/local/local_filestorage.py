import os
import shutil
import tempfile


class LocalFileStorage:
    def __init__(self, root_dir):

        self.root_dir = root_dir

    def upload_blob(self, src_file, destination_blob_name, mime_type):
        destination_blob_name = os.path.join(self.root_dir, destination_blob_name)

        self.upload_document(
            src_file,
            destination_blob_name,
            mime_type,
        )
        return f"{destination_blob_name}"

    def download_document(
        self,
        document_location,
        dest_file_location=None,
    ):

        if not os.path.isfile(document_location):
            ValueError("invalid local file location {doc_location_str}")

        if not document_location.startswith(self.root_dir):
            document_location = os.path.join(self.root_dir, document_location)

        if dest_file_location is None:
            dest_file_location_handler, dest_file_location = tempfile.mkstemp()
            os.close(dest_file_location_handler)
        shutil.copy(document_location, dest_file_location)
        return dest_file_location

    def download_from_location(self, document_location, fh):
        self.download_document(document_location, fh)

    def document_exists(self, document_location):

        if not document_location.startswith(self.root_dir):
            document_location = os.path.join(self.root_dir, document_location)

        return os.path.isfile(document_location)

    def upload_document(
        self,
        src_file_location,
        dest_document_location,
        mime_type=None,
    ):
        if not dest_document_location.startswith(self.root_dir):
            dest_document_location = os.path.join(self.root_dir, dest_document_location)

        blob = dest_document_location

        if not os.path.isfile(blob):
            ValueError("invalid local file location {doc_location_str}")
        os.makedirs(os.path.dirname(blob), exist_ok=True)
        shutil.copy(src_file_location, blob)

    def save_file_data(self, doc_id, file_data):
        tmpfile_handler, tmpfile_name = tempfile.mkstemp()
        os.close(tmpfile_handler)

        with open(tmpfile_name, "w") as f:
            f.write(file_data)

        dest_location = f"file_data/{doc_id}"
        self.upload_document(tmpfile_name, dest_location)

        if os.path.exists(tmpfile_name):
            os.unlink(tmpfile_name)

        return dest_location

    # legacy interface for IndexStorage
    def load_file(self, identifier):
        document_location = f"indexes/{identifier}"
        return self.download_document(document_location)

    # legacy interface for IndexStorage
    def save_file(self, identifier, src_file_location):
        dest_location = f"indexes/{identifier}"
        self.upload_document(src_file_location, dest_location)
