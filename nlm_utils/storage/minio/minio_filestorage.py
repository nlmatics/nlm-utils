import logging
import os
import tempfile

import urllib3
from minio import Minio
from minio.deleteobjects import DeleteObject


class MinIOFileStorage:
    def __init__(
        self,
        url=None,
        access_key=None,
        secret_key=None,
        bucket="doc-store-dev",
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        url = url or os.getenv("MINIO_URL", "localhost:9000")
        httpClient = urllib3.PoolManager(maxsize=1000)

        self.minioClient = Minio(
            url,
            access_key=access_key or os.getenv("MINIO_ACCESS", "user"),
            secret_key=secret_key or os.getenv("MINIO_SECRET", "password"),
            secure=False,
            http_client=httpClient,
        )
        self.bucket = bucket
        bucket_names = {item.name for item in self.minioClient.list_buckets()}
        if bucket not in bucket_names:
            self.logger.info(f"Bucket {bucket} does not exist!")
            self.minioClient.make_bucket(bucket)

    def upload_blob(self, src_file, destination_blob_name, mime_type):
        self.upload_document(src_file, destination_blob_name, mime_type)
        return f"{destination_blob_name}"

    def download_document(self, document_location, dest_file_location=None):
        document_location = document_location.replace(f"gs://{self.bucket}/", "")
        if self.document_exists(document_location):
            if dest_file_location is None:
                dest_file_location_handler, dest_file_location = tempfile.mkstemp()
                os.close(dest_file_location_handler)

            self.logger.info(
                f"Download document from {document_location} to {dest_file_location}",
            )
            self.minioClient.fget_object(
                self.bucket,
                document_location,
                dest_file_location,
            )
        else:
            raise Exception(
                f"Failed to download document from {document_location}. Document does not exists",
            )

        return dest_file_location

    def download_from_location(self, document_location, fh):
        self.download_document(document_location, fh)

    def document_exists(self, document_location):
        document_location = document_location.replace(f"gs://{self.bucket}/", "")
        try:
            self.minioClient.stat_object(self.bucket, document_location)
        except Exception:
            return False
        return True

    def upload_document(
        self,
        src_file_location,
        dest_document_location,
        mime_type="mime_type='application/octet-stream'",
    ):
        self.logger.info(f"Uploading {src_file_location} to {dest_document_location}")
        self.minioClient.fput_object(
            self.bucket,
            dest_document_location,
            src_file_location,
            content_type=mime_type,
        )

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

    def delete_files(self, file_prefix_list):
        """
        Delete the files whose prefixes matches the list provided
        :param file_prefix_list: List of file prefixes to delete
        :return:
        """
        for file_prefix in file_prefix_list:
            self.logger.info(f"Deleting files with prefix {file_prefix}")
            if file_prefix:
                names = map(
                    lambda x: DeleteObject(x.object_name),
                    self.minioClient.list_objects(
                        self.bucket,
                        file_prefix,
                        recursive=True,
                    ),
                )
                errors = self.minioClient.remove_objects(self.bucket, names)
                for error in errors:
                    self.logger.info(f"error occurred when deleting object. {error}")
