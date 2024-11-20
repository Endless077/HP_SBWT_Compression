import bitarray
import pickle
import random
import string
import os
from os import path

RANDOM_DIR_PATH: str = path.join(os.getcwd(), 'files', 'generated')
RANDOM_FILE_NAME: str = "{size}_random"


def _to_bytes(data: str) -> bytes:
    # get size of padding
    n_padding: int = 16 - (len(data) % 16)
    # convert size of padding in bytes
    n_padding_bytes: bytes = n_padding.to_bytes(1, 'big')
    # create bitarray from data + padding
    ba = bitarray.bitarray(data + '0' * n_padding)
    # return in bytes n_padding + data + padding
    return n_padding_bytes + ba.tobytes()


def _to_binary(data: bytes) -> str:
    # get size of padding
    n_padding: int = data[0]
    ba = bitarray.bitarray()
    # create bit array from bytes of data without n_padding
    ba.frombytes(data[1:])
    # convert to bitstring data without padding
    return ba.to01()[:-n_padding]


def generate_random_file(file_name: str, file_size: int, file_type: str = 'txt') -> str:
    assert '/' not in file_name

    os.makedirs(RANDOM_DIR_PATH, exist_ok=True)
    file_path: str = path.join(RANDOM_DIR_PATH, f"{file_name}.{file_type}")
    with open(file_path, 'w') as file:
        for _ in range(file_size):
            file.write(random.choice(string.ascii_letters))

    return file_path


def write_compressed_file_path_folder(file_path: str, file_name: str) -> str:
    assert '/' not in file_name

    os.makedirs(file_path, exist_ok=True)
    file_path: str = path.join(file_path, f"{file_name}.bin")
    return file_path


def write_decompressed_file_path_folder(file_path: str, file_name: str) -> str:
    assert '/' not in file_name

    os.makedirs(file_path, exist_ok=True)
    file_path: str = path.join(file_path, f"{file_name}.txt")
    return file_path


def write_compressed_file(file_path: str, file_name: str, data: str) -> str:
    assert '/' not in file_name

    os.makedirs(file_path, exist_ok=True)
    file_path: str = path.join(file_path, f"{file_name}.bin")
    with open(file_path, 'wb') as file:
        data_binary = _to_bytes(data)
        file.write(data_binary)

    return file_path


def write_compressed_file_bytes(file_path: str, file_name: str, data: bytes) -> str:
    assert '/' not in file_name

    os.makedirs(file_path, exist_ok=True)
    file_path: str = path.join(file_path, f"{file_name}.bin")
    with open(file_path, 'wb') as file:
        file.write(data)

    return file_path


def write_pickle(file_path: str, file_name: str, data) -> str:
    assert '/' not in file_name

    os.makedirs(file_path, exist_ok=True)
    file_path: str = path.join(file_path, f"{file_name}.bin")
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)

    return file_path


def read_pickle(file_path: str, file_name: str):
    assert '/' not in file_name

    file_path: str = path.join(file_path, f"{file_name}.bin")
    with open(file_path, 'rb') as file:
        return pickle.load(file)


def read_compressed_file(file_path: str, file_name: str) -> str:
    assert '/' not in file_name

    os.makedirs(file_path, exist_ok=True)
    file_path: str = path.join(file_path, f"{file_name}.bin")
    with open(file_path, 'rb') as file:
        data = file.read()
        data_binary = _to_binary(data)

    return data_binary


def read_compressed_file_bytes(file_path: str, file_name: str) -> bytes:
    assert '/' not in file_name

    os.makedirs(file_path, exist_ok=True)
    file_path: str = path.join(file_path, f"{file_name}.bin")
    with open(file_path, 'rb') as file:
        data = file.read()

    return data


def read_in_chunks(file_object, chunk_size=1024):
    """ Lazy function (generator) to read a file piece by piece. Default chunk size: 1k. """
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def write_decompressed_file(file_path: str, file_name: str, chunk: str) -> str:
    assert '/' not in file_name

    os.makedirs(file_path, exist_ok=True)
    file_path: str = path.join(file_path, f"{file_name}.txt")
    with open(file_path, 'a') as file:
        file.write(chunk)

    return file_path
