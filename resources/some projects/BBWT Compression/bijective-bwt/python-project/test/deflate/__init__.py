import os.path as path
import os

COMPRESSED_DEFLATE_DIR_PATH: str = path.join(os.getcwd(), 'compressed', 'deflate')
DECOMPRESSED_DEFLATE_DIR_PATH: str = path.join(os.getcwd(), 'decompressed', 'deflate')
COMPRESSED_DEFLATE_FILE_NAME: str = "{name}_{pre_processing}_deflate"


def generate_file_name(name: str, pre_processing: str) -> str:
    return COMPRESSED_DEFLATE_FILE_NAME.format(name=name, pre_processing=pre_processing)
