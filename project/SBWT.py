import logging
from collections import defaultdict
import numpy as np


# Funzione per costruire l'array dei suffissi con ordine personalizzato
def build_suffix_array_with_custom_order(s, custom_order):
    logging.debug("Inizio costruzione dell'array dei suffissi con ordine personalizzato.")
    n = len(s)
    suffix_array = np.arange(n, dtype=np.int32)
    rank = np.array([custom_order[c] for c in s], dtype=np.int32)

    k = 1
    while k < n:
        key = np.array([
            (rank[i], rank[i + k] if i + k < n else -1)
            for i in suffix_array
        ], dtype=[('rank1', int), ('rank2', int)])
        sorted_indices = np.argsort(key, order=['rank1', 'rank2'])
        suffix_array = suffix_array[sorted_indices]
        new_rank = np.zeros(n, dtype=np.int32)
        new_rank[suffix_array[0]] = 0
        for i in range(1, n):
            new_rank[suffix_array[i]] = new_rank[suffix_array[i - 1]] + (key[sorted_indices[i]] != key[sorted_indices[i - 1]])
        rank = new_rank
        k *= 2
    logging.debug("Array dei suffissi costruito con successo.")
    return suffix_array

# Funzione per generare ordine personalizzato con terminatore
def generate_random_order(input_string):
    logging.debug("Generazione dell'ordine personalizzato dei caratteri.")
    unique_chars = sorted(set(input_string + '\0'))
    order = {char: idx for idx, char in enumerate(unique_chars)}
    logging.debug(f"Ordine personalizzato generato: {order}")
    return order

# Funzione di compressione SBWT
def sbwt_compress(input_string):
    logging.debug("Inizio compressione SBWT.")
    if '\0' not in input_string:
        input_string += '\0'
        logging.debug("Carattere terminatore '\\0' aggiunto all'input.")
    custom_order = generate_random_order(input_string)
    suffix_array = build_suffix_array_with_custom_order(input_string, custom_order)
    last_column = ''.join(input_string[i - 1] for i in suffix_array)
    try:
        orig_ptr = int(np.where(suffix_array == 0)[0][0])
    except IndexError:
        logging.error("orig_ptr non trovato nell'array dei suffissi.")
        orig_ptr = 0  # Valore di default o gestisci l'errore come preferisci
    logging.debug("Compressione SBWT completata.")
    return last_column, orig_ptr, custom_order

# Funzione di decompressione SBWT
def sbwt_decompress(last_column, orig_ptr, custom_order):
    logging.debug("Inizio decompressione SBWT.")
    n = len(last_column)
    first_col = ''.join(sorted(last_column, key=lambda c: (custom_order[c], c)))

    count_last = defaultdict(int)
    first_indices = defaultdict(list)
    for idx, char in enumerate(first_col):
        first_indices[char].append(idx)

    last_to_first = [-1] * n
    for idx, char in enumerate(last_column):
        last_to_first[idx] = first_indices[char][count_last[char]]
        count_last[char] += 1

    original = []
    idx = orig_ptr
    for _ in range(n):
        original.append(last_column[idx])
        idx = last_to_first[idx]

    decompressed = ''.join(reversed(original)).rstrip('\0')
    logging.debug("Decompressione SBWT completata.")
    return decompressed

# Funzione per salvare l'ordine personalizzato
def save_custom_order(f, custom_order):
    logging.debug("Salvataggio dell'ordine personalizzato dei caratteri.")
    # Salva la lunghezza dell'ordine personalizzato
    f.write(len(custom_order).to_bytes(2, byteorder='big'))
    for char, idx in custom_order.items():
        char_bytes = char.encode('utf-8')
        # Salva la lunghezza del carattere
        f.write(len(char_bytes).to_bytes(1, byteorder='big'))
        # Salva il carattere
        f.write(char_bytes)
        # Salva l'indice come 4 byte interi
        f.write(idx.to_bytes(4, byteorder='big'))
    logging.debug("Ordine personalizzato dei caratteri salvato con successo.")

# Funzione per caricare l'ordine personalizzato
def load_custom_order(f):
    logging.debug("Caricamento dell'ordine personalizzato dei caratteri.")
    custom_order_length = int.from_bytes(f.read(2), byteorder='big')
    custom_order = {}
    for _ in range(custom_order_length):
        # Leggi la lunghezza del carattere
        char_length = int.from_bytes(f.read(1), byteorder='big')
        # Leggi il carattere
        char_bytes = f.read(char_length)
        char = char_bytes.decode('utf-8')
        # Leggi l'indice (4 byte)
        idx = int.from_bytes(f.read(4), byteorder='big')
        custom_order[char] = idx
    logging.debug("Ordine personalizzato dei caratteri caricato con successo.")
    return custom_order