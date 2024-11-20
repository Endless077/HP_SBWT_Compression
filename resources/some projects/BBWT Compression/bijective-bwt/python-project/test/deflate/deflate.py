from test.deflate import COMPRESSED_DEFLATE_DIR_PATH
from test.deflate import DECOMPRESSED_DEFLATE_DIR_PATH
from test.deflate import generate_file_name

from compression.deflate import deflate as deflate_encoding
from compression.deflate import inflate as deflate_decoding

from util.file import write_compressed_file_bytes
from util.file import read_compressed_file_bytes
from util.file import write_decompressed_file


import os

PRE_PROCESSING: str = ""


def deflate(file_path: str, file_name: str):
    # open and read file
    _file = open(os.path.join(file_path, file_name))
    data = _file.read()
    data = data.encode()

    # generate file name of compressed file
    _file_name: str = os.path.splitext(file_name)[0]
    compressed_file_name: str = generate_file_name(_file_name, PRE_PROCESSING)

    # use deflate encoding
    compressed_data = deflate_encoding(data)

    # write compressed file
    write_compressed_file_bytes(COMPRESSED_DEFLATE_DIR_PATH, compressed_file_name, compressed_data)
    # read compressed file
    compressed_data: str = read_compressed_file_bytes(COMPRESSED_DEFLATE_DIR_PATH, compressed_file_name)

    # use deflate decoding
    decompressed_data = deflate_decoding(compressed_data)
    # convert decompressed_data to text
    _data = decompressed_data.decode("utf-8")
    write_decompressed_file(DECOMPRESSED_DEFLATE_DIR_PATH, compressed_file_name, _data)

    return os.path.join(COMPRESSED_DEFLATE_DIR_PATH, compressed_file_name)
