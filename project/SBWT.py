import logging
from collections import defaultdict
import numpy as np
import hashlib

# Funzione per generare l'ordine personalizzato basato sulla chiave
def generate_order_from_key(input_string, key):
    logging.debug("Generazione dell'ordine personalizzato basato sulla chiave.")
    unique_chars = sorted(set(input_string + '\0'))
    key_bytes = key.encode('utf-8')
    char_hashes = []
    for c in unique_chars:
        # Combina la chiave con il carattere
        combined = key_bytes + c.encode('utf-8')
        # Calcola l'hash SHA-256
        hash_value = hashlib.sha256(combined).hexdigest()
        char_hashes.append((c, hash_value))
    # Ordina i caratteri in base al valore hash
    sorted_chars = sorted(char_hashes, key=lambda x: x[1])
    # Assegna l'ordine
    order = {char: idx for idx, (char, _) in enumerate(sorted_chars)}
    logging.debug(f"Ordine personalizzato generato basato sulla chiave: {order}")
    return order

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

# Funzione di compressione SBWT
def sbwt_compress(input_string, key):
    logging.debug("Inizio compressione SBWT.")
    if '\0' not in input_string:
        input_string += '\0'
        logging.debug("Carattere terminatore '\\0' aggiunto all'input.")
    custom_order = generate_order_from_key(input_string, key)
    suffix_array = build_suffix_array_with_custom_order(input_string, custom_order)
    last_column = ''.join(input_string[i - 1] for i in suffix_array)
    try:
        orig_ptr = int(np.where(suffix_array == 0)[0][0])
    except IndexError:
        logging.error("orig_ptr non trovato nell'array dei suffissi.")
        orig_ptr = 0  # Valore di default o gestisci l'errore come preferisci
    logging.debug("Compressione SBWT completata.")
    return last_column, orig_ptr

# Funzione di decompressione SBWT
def sbwt_decompress(last_column, orig_ptr, key):
    logging.debug("Inizio decompressione SBWT.")
    n = len(last_column)
    custom_order = generate_order_from_key(last_column, key)
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

# Funzione per salvare l'ordine personalizzato (rimossa)
# Funzione per caricare l'ordine personalizzato (rimossa)