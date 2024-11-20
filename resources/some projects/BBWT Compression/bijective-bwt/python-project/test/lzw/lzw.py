from test.lzw import COMPRESSED_LZW_DIR_PATH
from test.lzw import DECOMPRESSED_LZW_DIR_PATH
from test.lzw import generate_file_name

from compression.lzw import lzw_encoding
from compression.lzw import lzw_decoding

from util.file import write_pickle
from util.file import read_pickle
from util.file import write_decompressed_file

import os

PRE_PROCESSING: str = ""


def lzw(file_path: str, file_name: str):
    # open and read file
    _file = open(os.path.join(file_path, file_name))
    data = _file.read()

    # generate file name of compressed file
    _file_name: str = os.path.splitext(file_name)[0]
    compressed_file_name: str = generate_file_name(_file_name, PRE_PROCESSING)

    # use lzw encoding
    compressed_data = lzw_encoding(data)
    # write compressed file
    write_pickle(COMPRESSED_LZW_DIR_PATH, compressed_file_name, compressed_data)

    # read compressed file
    compressed_data: str = read_pickle(COMPRESSED_LZW_DIR_PATH, compressed_file_name)

    # use lzw decoding
    decompressed_data = lzw_decoding(compressed_data)

    _data: str = ''.join([str(item) for item in decompressed_data])
    write_decompressed_file(DECOMPRESSED_LZW_DIR_PATH, compressed_file_name, _data)

    return os.path.join(COMPRESSED_LZW_DIR_PATH, compressed_file_name)
