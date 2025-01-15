# High Performance SBWT 📦🔑

High Performance SBWT is a Python-based project that implements a cryptographic compression pipeline using advanced algorithms such as SBWT, Huffman coding, Arithmetic coding, LZW, and BZip2. It provides tools for compressing and encrypting data with a modular and extensible approach.


## 🔑 Key Features

- ***User-Friendly***: Command-line interface for easy usage and configuration.

- ***Benchmarking Tools***: Comes with utilities for testing and comparing performance.

- ***Pipeline Integration***: Implements SBWT-based cryptographic compression pipeline.

- ***Multi-Algorithm Support***: Includes Huffman, Arithmetic coding, BZip2, and LZW.


## 🛠️ Installation

### 📋 Prerequisites

Ensure you have the following installed:

- Python 3.8+: Download it from python.org.

### ⚙️ Installation Steps

1. Install Dependencies:
  Install required packages from requirements.txt:
  ```bash
  pip install -r requirements.txt
  ```

2. Verify Installation:
  Check the help options for the main scripts:
  ```bash
  python3 hpswbt.py -h
  python3 testing.py -h
  ```

### ⚠️ Notes

Ensure you have sufficient disk space for benchmarking large datasets.


## 📜 Usage

1. Compress and Encrypt
  Run the main script with desired options:
  ```bash
  python3 hpswbt.py compress -i input -m mode -k key [-l log]
  python3 hpswbt.py decompress -i input -o output -k key [-l log]
  ```

2. Benchmarking
  Use the testing.py script to evaluate performance:
  ```bash
  python3 testing.py -i input -m mode -k key [-l log]
  ```


## 📜 API Reference

- ***hpswbt.py***:
  Implements the cryptographic compression pipeline.
  Options for selecting algorithms: huffman, arithmetic, lzw, bzip2.

- ***testing.py***:
  Provides benchmarking utilities for testing performance and compression ratios.

- ***Other Modules***:
  Additional modules are available separately for modular usage.


## 🙏 Acknowledgements

### Huffman Coding 🌲

Huffman coding is a lossless data compression algorithm.

### Arithmetic Coding 🔢

Arithmetic coding provides high compression ratios for specific data types.

### BZip2 🗜️

BZip2 is a block-sorting compression algorithm for high efficiency.

### LZW 🔡

LZW is a simple and fast algorithm widely used in file formats like GIF.

### SBWT 📊

SBWT is a method used for data transformations in the pipeline.


## 💾 License

This project is licensed under the GNU General Public License v3.0.

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)

![Static Badge](https://img.shields.io/badge/UniSA-HPSBWT-red?style=plastic)


## 🖐 Author

**Contributors:**
- [Fulvio Serao](https://github.com/Fulvioserao99)
- [Marco Fusco](https://github.com/3VOLTE6)
- [Marco Palmisciano](https://github.com/JewDaiko)

**Project Manager:**
- [Antonio Garofalo](https://github.com/Endless077)


## 🔔 Support

For support, email [antonio.garofalo125@gmail.com](mailto:antonio.garofalo125@gmail.com) or contact the project contributors.


## 📝 Documentation

See the documentation project **[here](https://github.com/Endless077/HP_SBWT_Compression/blob/main/paper.pdf)**.
