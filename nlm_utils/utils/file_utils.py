import hashlib
import json
import logging
import magic
import os
import dicttoxml
from datetime import datetime


dicttoxml.LOG.setLevel(logging.ERROR)


def get_file_sha256(filepath):
    """Calculates the SHA256 hash of the file contents
    :param filepath:
    :return:
    """
    sha2 = hashlib.sha256()
    with open(filepath, "rb") as fh:
        buf_size = 131072  # 128kb
        while True:
            data = fh.read(buf_size)
            if not data:
                break
            sha2.update(data)
    return sha2.hexdigest()


def convert_json_to_xml(file_name):
    """
    Convert the JSON to XML and rewrite the data to XML in the same file
    :param file_name:
    :return: Void
    """
    with open(file_name, "r+") as f:
        data = f.read()
        xml = dicttoxml.dicttoxml(json.loads(data))
        xml_decode = xml.decode()
        f.seek(0)
        f.write(xml_decode)
        f.truncate()


def extract_file_properties(filepath):
    if filepath.endswith(".md"):
        mime_type = "text/x-markdown"
    elif filepath.endswith(".html"):
        mime_type = "text/html"
    elif filepath.endswith(".pdf"):
        mime_type = "application/pdf"
    elif filepath.endswith(".xml"):
        mime_type = "text/xml"
    else:
        mime_type = magic.from_file(filepath, mime=True)
    file_size = os.path.getsize(filepath)
    checksum = get_file_sha256(filepath)
    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "fileSize": file_size,
        "mimeType": mime_type,
        "checksum": checksum,
        "createdOn": creation_date,
        "isDeleted": False,
    }

