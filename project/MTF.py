import logging
from collections import defaultdict, Counter


# Move-to-Front Encoding
def move_to_front_encode(data):
    logging.debug("Inizio encoding Move-to-Front (MTF).")
    symbols = sorted(set(data))
    mtf_list = symbols[:]
    encoded = []
    for char in data:
        try:
            index = mtf_list.index(char)
        except ValueError:
            logging.error(f"Carattere '{char}' non trovato nella lista MTF.")
            index = 0  # Gestione del carattere mancante
        encoded.append(index)
        mtf_list.pop(index)
        mtf_list.insert(0, char)
    logging.debug("Encoding MTF completato.")
    return encoded, symbols

# Move-to-Front Decoding
def move_to_front_decode(encoded, symbols):
    logging.debug("Inizio decoding Move-to-Front (MTF).")
    mtf_list = symbols[:]
    decoded = []
    for index in encoded:
        if index < 0 or index >= len(mtf_list):
            logging.error(f"Indice MTF invalido: {index}")
            char = symbols[0]  # Gestione dell'indice invalido
        else:
            char = mtf_list[index]
        decoded.append(char)
        mtf_list.pop(index)
        mtf_list.insert(0, char)
    logging.debug("Decoding MTF completato.")
    return ''.join(decoded)

# Funzione per salvare i simboli MTF
def save_symbols(f, symbols):
    logging.debug("Salvataggio dei simboli Move-to-Front (MTF).")
    # Salva la lunghezza dei simboli
    f.write(len(symbols).to_bytes(2, byteorder='big'))
    for symbol in symbols:
        symbol_bytes = symbol.encode('utf-8')
        # Salva la lunghezza del simbolo
        f.write(len(symbol_bytes).to_bytes(1, byteorder='big'))
        # Salva il simbolo
        f.write(symbol_bytes)
    logging.debug("Simboli MTF salvati con successo.")

# Funzione per caricare i simboli MTF
def load_symbols(f):
    logging.debug("Caricamento dei simboli Move-to-Front (MTF).")
    symbols_length = int.from_bytes(f.read(2), byteorder='big')
    symbols = []
    for _ in range(symbols_length):
        # Leggi la lunghezza del simbolo
        symbol_length = int.from_bytes(f.read(1), byteorder='big')
        # Leggi il simbolo
        symbol_bytes = f.read(symbol_length)
        symbol = symbol_bytes.decode('utf-8')
        symbols.append(symbol)
    logging.debug("Simboli MTF caricati con successo.")
    return symbols