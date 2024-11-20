import matplotlib.pyplot as plt
import numpy as np
import os


def plot_different_chunk_size(file_name: str, algorithm: str, chunk_size: int, results: [dict]):
    os.makedirs('images', exist_ok=True)
    _file_name = f'{file_name}_{chunk_size}_{algorithm}.jpg'
    file_path: str = os.path.join('images', _file_name)

    # create data
    ratios = [r["RATIO"] for r in results]
    pipelines = [r["PIPELINE"] for r in results]
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

    plt.title(file_name)
    plt.xlabel('pipeline')
    plt.ylabel('compression ratio')

    # print value on the top of bar
    x_locs, x_labs = plt.xticks()
    for i, v in enumerate(ratios):
        plt.text(x_locs[i] - 0.12, v + 0.05, str(v))

    # set limit on y label
    plt.ylim(0, max(ratios) + 0.3)

    # savefig
    plt.savefig(file_path)
    plt.clf()


def plot_different_pipeline(file_name: str, pipeline: str, results: [dict], chunks):
    os.makedirs('images', exist_ok=True)
    _file_name = f'{file_name}_{pipeline}.jpg'
    file_path: str = os.path.join('images', _file_name)

    # create data
    ratios = [r["RATIO"] for r in results]

    x_pos = np.arange(len(chunks))

    # create bars
    plt.bar(x_pos, ratios, width=0.5)

    # rotation of the bar names
    plt.xticks(x_pos, chunks, rotation=90)
    # custom the subplot layout
    plt.subplots_adjust(bottom=0.2, top=0.9)
    # enable grid
    plt.grid(True)

    plt.title(pipeline)
    plt.xlabel('chunk size')
    plt.ylabel('compression ratio')

    # print value on the top of bar
    x_locs, x_labs = plt.xticks()
    for i, v in enumerate(ratios):
        plt.text(x_locs[i] - 0.22, v + 0.05, str(v))

    # set limit on y label
    plt.ylim(0, max(ratios) + 0.3)

    # savefig
    plt.savefig(file_path)
    plt.clf()
