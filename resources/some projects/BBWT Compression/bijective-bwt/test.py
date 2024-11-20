from matplotlib import pyplot as plt
import os.path as path
import numpy as np
import time
import os

def generate_file_name(name: str,pipeline: str) -> str:
    return f"{name}_{pipeline}"


def compression_ratio_from_file(uncompressed_path: str, compressed_path: str, decimal_digits=2) -> float:
    uncompressed_size = os.path.getsize(uncompressed_path)
    compressed_size = os.path.getsize(compressed_path)
    
    if compressed_size == 0:
        return 0

    return round(uncompressed_size / compressed_size, decimal_digits)


def plot_compression_ratio(file_name: str, algorithm: str, results: [dict]):
    os.makedirs('images', exist_ok=True)
    _file_name = f'{file_name}_{algorithm}_ratio.svg'
    file_path: str = os.path.join('images', _file_name)

    # create data
    ratios = [r["compression_ratio"] for r in results]
    pipelines = [
        "-", 
        "BWT M2F", 
        "BBWT M2F", 
        "BWT M2F RLE", 
        "BBWT M2F RLE", 
        "RLE BWT M2F RLE", 
        "RLE BBWT M2F RLE"]
    x_pos = np.arange(len(pipelines))

    # create bars
    plt.bar(x_pos, ratios, width=0.5)

    # rotation of the bar names
    plt.xticks(x_pos, pipelines, rotation=90)
    # custom the subplot layout
    if algorithm == 'arithmetic_code':
        plt.subplots_adjust(bottom=0.6, top=0.9)
    else:
        plt.subplots_adjust(bottom=0.4, top=0.9)
    # enable grid
    plt.grid(True)

    plt.title(f'{file_name}: {algorithm}')
    plt.xlabel('Pipeline')
    plt.ylabel('Compression ratio')

    # print value on the top of bar
    x_locs, x_labs = plt.xticks()
    for i, v in enumerate(ratios):
        plt.text(x_locs[i] - 0.2, v + 0.05, str(v))

    # set limit on y label
    plt.ylim(0, max(ratios) + 0.3)

    # savefig
    plt.savefig(file_path)
    plt.clf()


def plot_time_different_pipeline(file_name: str, algorithm: str, results: [dict]):
    os.makedirs('images', exist_ok=True)
    _file_name = f'{file_name}_{algorithm}_time.svg'
    file_path: str = os.path.join('images', _file_name)

    # create data
    compression_time = [r["compression_time"] for r in results]
    decompression_time = [r["decompression_time"] for r in results]
    pipelines = [
        "-", 
        "BWT M2F", 
        "BBWT M2F", 
        "BWT M2F RLE", 
        "BBWT M2F RLE", 
        "RLE BWT M2F RLE", 
        "RLE BBWT M2F RLE"]
    x_pos = np.arange(len(pipelines))

    # create grouped bars
    width = 0.35
    fig, ax = plt.subplots()
    rects1 = ax.bar(x_pos - width / 2, compression_time, width, label='Compression time')
    rects2 = ax.bar(x_pos + width / 2, decompression_time, width, label='Decompression time')

    # rotation of the bar names
    plt.xticks(x_pos, pipelines, rotation=90)
    ax.legend()
    # enable grid
    plt.grid(True)

    plt.title(f'{file_name}: {algorithm}')
    plt.xlabel('Pipeline')
    plt.ylabel('Time in ms')

    # print value on the top of bar
    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    # set limit on y label
    ax.margins(y=0.2)

    # savefig
    fig.tight_layout()
    plt.savefig(file_path)
    plt.clf()


COMPRESSED_DIR_PATH: str = path.join(os.getcwd(), 'compressed')
DECOMPRESSED_DIR_PATH: str = path.join(os.getcwd(), 'decompressed')
PATH_DIR_TEST_FILES = os.path.join(os.getcwd(), "files")

PIPELINES = [
    "HUFFMAN",
    "ARITHMETIC_CODE",                     
    "BWT_M2F_HUFFMAN",                     
    "BWT_M2F_ARITHMETIC_CODE",           
    "BBWT_M2F_HUFFMAN",                  
    "BBWT_M2F_ARITHMETIC_CODE",            
    "BWT_M2F_RLE_HUFFMAN",                
    "BWT_M2F_RLE_ARITHMETIC_CODE",       
    "BBWT_M2F_RLE_HUFFMAN",             
    "BBWT_M2F_RLE_ARITHMETIC_CODE",        
    "RLE_BWT_M2F_RLE_HUFFMAN",           
    "RLE_BWT_M2F_RLE_ARITHMETIC_CODE",   
    "RLE_BBWT_M2F_RLE_HUFFMAN",          
    "RLE_BBWT_M2F_RLE_ARITHMETIC_CODE",
    "LZW_HUFFMAN",
    "BWT_M2F_LZW_HUFFMAN",
    "BBWT_M2F_LZW_HUFFMAN",
    "BWT_M2F_RLE_LZW_HUFFMAN",                
    "BBWT_M2F_RLE_LZW_HUFFMAN",                
    "RLE_BWT_M2F_RLE_LZW_HUFFMAN",           
    "RLE_BBWT_M2F_RLE_LZW_HUFFMAN",           
]    


if __name__ == "__main__":

    os.system('rm -r compressed decompressed images')
    os.makedirs(COMPRESSED_DIR_PATH, exist_ok = True)
    os.makedirs(DECOMPRESSED_DIR_PATH, exist_ok = True)

    map_results_huffman = []
    map_results_arith = []
    map_results_lzw_huffman = []

    for file_name in os.listdir(PATH_DIR_TEST_FILES):

        for pipe in range(len(PIPELINES)):

            if pipe < 14:
                continue

            abspath_file = os.path.join(PATH_DIR_TEST_FILES, file_name)
            abspath_compressed_file = os.path.join(COMPRESSED_DIR_PATH, generate_file_name(os.path.splitext(file_name)[0],PIPELINES[pipe]))
            abspath_decompressed_file = os.path.join(DECOMPRESSED_DIR_PATH, generate_file_name(os.path.splitext(file_name)[0],PIPELINES[pipe]))

            # compression test
            start_time = time.time()
            os.system(f'./main -c {pipe} {abspath_file} {abspath_compressed_file}')
            compression_time = round((time.time() - start_time) * 1000)

            # decompression test
            start_time = time.time()
            os.system(f'./main -d {pipe} {abspath_compressed_file} {abspath_decompressed_file}')
            decompression_time = round((time.time() - start_time) * 1000)
            
            if (pipe > 13):
                result_lzw_huffman = dict()
                result_lzw_huffman["filename"] = file_name
                result_lzw_huffman["pipeline"] = PIPELINES[pipe]
                result_lzw_huffman["compression_ratio"] = compression_ratio_from_file(abspath_file,abspath_compressed_file)
                result_lzw_huffman["compression_time"] = compression_time
                result_lzw_huffman["decompression_time"] = decompression_time
                map_results_lzw_huffman.append(result_lzw_huffman)

            else:

                if (PIPELINES[pipe].find("HUFFMAN") != -1):
                    result_huffman = dict()
                    result_huffman["filename"] = file_name
                    result_huffman["pipeline"] = PIPELINES[pipe]
                    result_huffman["compression_ratio"] = compression_ratio_from_file(abspath_file,abspath_compressed_file)
                    result_huffman["compression_time"] = compression_time
                    result_huffman["decompression_time"] = decompression_time
                    map_results_huffman.append(result_huffman)

                else:
                    result_arith = dict()
                    result_arith["pipeline"] = PIPELINES[pipe]
                    result_arith["compression_ratio"] = compression_ratio_from_file(abspath_file,abspath_compressed_file)
                    result_arith["compression_time"] = compression_time
                    result_arith["filename"] = file_name
                    result_arith["decompression_time"] = decompression_time
                    map_results_arith.append(result_arith)
        
        plot_compression_ratio(file_name, "huffman", map_results_huffman)
        plot_compression_ratio(file_name, "arithmetic code", map_results_arith)
        plot_compression_ratio(file_name, "lzw huffman", map_results_lzw_huffman)

        plot_time_different_pipeline(file_name, "huffman", map_results_huffman)
        plot_time_different_pipeline(file_name, "arithmetic code", map_results_arith)
        plot_time_different_pipeline(file_name, "lzw huffman", map_results_lzw_huffman)

        map_results_arith.clear()
        map_results_huffman.clear()
        map_results_lzw_huffman.clear()
