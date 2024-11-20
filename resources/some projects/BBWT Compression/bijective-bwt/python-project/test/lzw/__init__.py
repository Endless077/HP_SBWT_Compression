import os.path as path
import os

COMPRESSED_LZW_DIR_PATH: str = path.join(os.getcwd(), 'compressed', 'lzw')
DECOMPRESSED_LZW_DIR_PATH: str = path.join(os.getcwd(), 'decompressed', 'lzw')
COMPRESSED_LZW_FILE_NAME: str = "{name}_{pre_processing}_lzw"


def generate_file_name(name: str, pre_processing: str) -> str:
    return COMPRESSED_LZW_FILE_NAME.format(name=name, pre_processing=pre_processing)
