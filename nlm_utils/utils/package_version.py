"""
Code from https://github.com/cakepietoast/checksumdir under MIT license

Function for deterministically creating a single hash for a directory of files,
taking into account only file contents and not filenames.
Usage:
from checksumdir import dirhash
dirhash('/path/to/directory', 'md5')
"""
import hashlib
import os
import re

import xxhash

HASH_FUNCS = {
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
    "xxh32": xxhash.xxh32,
    "xxh64": xxhash.xxh64,
}


def dirhash(
    dirname,
    hashfunc="xxh32",
    excluded_files=None,
    ignore_hidden=True,
    followlinks=False,
    excluded_extensions=["pyc"],
    include_paths=False,
):
    hash_func = HASH_FUNCS.get(hashfunc)
    if not hash_func:
        raise NotImplementedError(f"{hashfunc} not implemented.")

    if not excluded_files:
        excluded_files = []

    if not excluded_extensions:
        excluded_extensions = []

    if not os.path.isdir(dirname):
        raise TypeError(f"{dirname} is not a directory.")

    hashvalues = []
    for root, dirs, files in os.walk(dirname, topdown=True, followlinks=followlinks):
        if ignore_hidden and re.search(r"/\.", root):
            continue

        dirs.sort()
        files.sort()
        # print("dirs", dirs)
        # print("files", files)
        # print()

        for fname in files:
            if ignore_hidden and fname.startswith("."):
                continue

            if fname.split(".")[-1:][0] in excluded_extensions:
                continue

            if fname in excluded_files:
                continue

            hashvalues.append(_filehash(os.path.join(root, fname), hash_func))

            if include_paths:
                hasher = hash_func()
                # get the resulting relative path into array of elements
                path_list = os.path.relpath(os.path.join(root, fname)).split(os.sep)
                # compute the hash on joined list, removes all os specific separators
                hasher.update("".join(path_list).encode("utf-8"))
                hashvalues.append(hasher.hexdigest())

    return hashvalues


def _filehash(filepath, hashfunc):
    hasher = hashfunc()
    blocksize = 64 * 1024

    if not os.path.exists(filepath):
        return hasher.hexdigest()

    with open(filepath, "rb") as fp:
        while True:
            data = fp.read(blocksize)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def _reduce_hash(hashlist, hashfunc):
    hasher = hashfunc()
    for hashvalue in sorted(hashlist):
        hasher.update(hashvalue.encode("utf-8"))
    return hasher.hexdigest()


def generate_version(
    paths,
    main_version=None,
    version_file="version.txt",
    hashfunc="xxh32",
):

    if main_version is None:
        main_version = "0.0.0"
        try:
            for version_file in [os.path.join(path, version_file) for path in paths] + [
                version_file,
            ]:
                with open(version_file) as f:
                    main_version = f.read().strip()
                break
        except FileNotFoundError:
            pass

    hashvalues = []
    if isinstance(paths, str):
        paths = [paths]

    for path in paths:
        hashvalues += dirhash(path, hashfunc=hashfunc)

    hash_func = HASH_FUNCS.get(hashfunc)
    code_version = _reduce_hash(hashvalues, hash_func)

    return f"{main_version}+{code_version}"
