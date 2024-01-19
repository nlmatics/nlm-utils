import os
from multiprocessing import Value

from .local.local_filestorage import LocalFileStorage
from .minio.minio_filestorage import MinIOFileStorage


PLATFORM = os.getenv("PLATFORM", "local")
if PLATFORM == "cloud":
    file_storage = MinIOFileStorage(bucket=os.getenv("STORAGE_NAME", "doc-store-dev"))
elif PLATFORM == "local":
    file_storage = LocalFileStorage(root_dir=os.getenv("STORAGE_NAME", "/doc-store"))
else:
    raise OSError(
        f"PLATFORM: {PLATFORM} is not supported yet. Please set it to 'cloud' or 'local'",
    )
