import logging
from collections import Counter
import heapq
import math

# Classe Nodo per Huffman
class HuffmanNode:
    def __init__(self, symbol=None, freq=0):
        self.symbol = symbol
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

# Costruzione dell'albero di Huffman
def build_huffman_tree(data):
    logging.debug("Inizio costruzione dell'albero di Huffman.")
    frequency = Counter(data)
    heap = [HuffmanNode(symbol, freq) for symbol, freq in frequency.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(freq=left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
    logging.debug("Albero di Huffman costruito con successo.")
    return heap[0]

# Generazione dei codici di Huffman
def build_huffman_codes(root):
    logging.debug("Inizio generazione dei codici di Huffman.")
    codes = {}
    def generate_codes(node, current_code):
        if node is None:
            return
        if node.symbol is not None:
            codes[node.symbol] = current_code
        generate_codes(node.left, current_code + "0")
        generate_codes(node.right, current_code + "1")
    generate_codes(root, "")
    logging.debug("Codici di Huffman generati con successo.")
    return codes

# Codifica di Huffman ottimizzata
def huffman_encode(data):
    logging.debug("Inizio codifica di Huffman.")
    root = build_huffman_tree(data)
    huffman_codes = build_huffman_codes(root)
    encoded_bits = ''.join(huffman_codes[symbol] for symbol in data)

    # Aggiungi padding per rendere la lunghezza multipla di 8
    padding_length = 8 - (len(encoded_bits) % 8) if len(encoded_bits) % 8 != 0 else 0
    encoded_bits += '0' * padding_length

    # Converti la stringa di bit in byte
    encoded_bytes = bytearray()
    for i in range(0, len(encoded_bits), 8):
        byte = encoded_bits[i:i+8]
        encoded_bytes.append(int(byte, 2))

    logging.debug("Codifica di Huffman completata.")
    return encoded_bytes, huffman_codes, padding_length

# Decodifica di Huffman ottimizzata
def huffman_decode(encoded_bytes, huffman_codes, padding_length):
    logging.debug("Inizio decodifica di Huffman.")
    # Converti i byte in stringa di bit
    encoded_bits = ''.join(f'{byte:08b}' for byte in encoded_bytes)

    # Rimuovi il padding
    if padding_length > 0:
        encoded_bits = encoded_bits[:-padding_length]

    reverse_codes = {v: k for k, v in huffman_codes.items()}
    decoded = []
    current_code = ""
    for bit in encoded_bits:
        current_code += bit
        if current_code in reverse_codes:
            decoded.append(reverse_codes[current_code])
            current_code = ""
    logging.debug("Decodifica di Huffman completata.")
    return decoded

# Funzione per salvare i codici di Huffman in modo efficiente (simboli interi)
def save_huffman_codes(f, huffman_codes):
    logging.debug("Salvataggio dei codici di Huffman.")
    # Salva la lunghezza dei codici di Huffman
    f.write(len(huffman_codes).to_bytes(2, byteorder='big'))
    for symbol, code in huffman_codes.items():
        # Salva il simbolo come 4 byte interi
        f.write(symbol.to_bytes(4, byteorder='big'))
        
        # Salva la lunghezza del codice
        code_length = len(code)
        f.write(code_length.to_bytes(1, byteorder='big'))
        
        # Salva il codice come byte
        code_bytes_length = math.ceil(code_length / 8)
        code_int = int(code, 2)
        code_bytes = code_int.to_bytes(code_bytes_length, byteorder='big')
        f.write(code_bytes)
    logging.debug("Codici di Huffman salvati con successo.")

# Funzione per caricare i codici di Huffman (simboli interi)
def load_huffman_codes(f):
    logging.debug("Caricamento dei codici di Huffman.")
    huffman_codes_length = int.from_bytes(f.read(2), byteorder='big')
    huffman_codes = {}
    for _ in range(huffman_codes_length):
        # Leggi il simbolo (4 byte)
        symbol = int.from_bytes(f.read(4), byteorder='big')
        
        # Leggi la lunghezza del codice
        code_length = int.from_bytes(f.read(1), byteorder='big')
        
        # Leggi il codice
        code_bytes_length = math.ceil(code_length / 8)
        code_bytes = f.read(code_bytes_length)
        code_int = int.from_bytes(code_bytes, byteorder='big')
        code = bin(code_int)[2:].zfill(code_length)
        
        huffman_codes[symbol] = code
    logging.debug("Codici di Huffman caricati con successo.")
    return huffman_codes