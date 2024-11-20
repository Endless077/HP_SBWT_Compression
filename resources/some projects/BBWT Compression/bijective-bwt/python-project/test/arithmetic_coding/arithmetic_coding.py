from test.arithmetic_coding import COMPRESSED_ARITHMETIC_CODING_DIR_PATH
from test.arithmetic_coding import DECOMPRESSED_ARITHMETIC_CODING_DIR_PATH
from test.arithmetic_coding import generate_file_name

from compression.arithmetic_coding import arithmetic_encoding
from compression.arithmetic_coding import arithmetic_decoding

from util.file import write_compressed_file_path_folder
from util.file import write_decompressed_file

from util.file_compare import compression_ratio_from_file

import os

PRE_PROCESSING: str = ""


def arithmetic_coding(file_path: str, file_name: str) -> str:
    # open and read file
    input_file_path = os.path.join(file_path, file_name)

    # generate file name and file path of compressed file
    _file_name: str = os.path.splitext(file_name)[0]
    compressed_file_name: str = generate_file_name(_file_name, PRE_PROCESSING, 0)
    compressed_file_path: str = write_compressed_file_path_folder(COMPRESSED_ARITHMETIC_CODING_DIR_PATH,
                                                                  compressed_file_name)

    # use arithmetic encoding and write compressed file
    os.system(f'./ac/arithm-coding e {input_file_path} {compressed_file_path}')

    # decompress with arithmetic coding
    decompressed_file_path: str = os.path.join(DECOMPRESSED_ARITHMETIC_CODING_DIR_PATH, f"{compressed_file_name}.txt")
    os.system(f'./ac/arithm-coding d {compressed_file_path} {decompressed_file_path}')

    compression_ratio = compression_ratio_from_file(os.path.join(file_path, file_name),
                                                    compressed_file_path)
    result = dict()
    result["PIPELINE"] = PRE_PROCESSING + 'arithmetic_coding'
    result["RATIO"] = compression_ratio
    result["PATH"] = compressed_file_path
    return result
