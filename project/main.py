import numpy as np
import logging
import os
import time  # Importazione del modulo time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import SBWT as sbwt
import MTF as mtf
import Huffman as huff
import sys  # Importato per gestire gli argomenti della riga di comando

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,  # Impostato su INFO per ridurre l'overhead
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Definizione della dimensione del blocco (64 KB)
BLOCK_SIZE = 64 * 1024  # 64 KB

# Compressione e decompressione aggiornate
def compress_data(input_data, key):
    logging.debug("Inizio processo di compressione dei dati.")
    last_column, orig_ptr = sbwt.sbwt_compress(input_data, key)
    mtf_encoded, symbols = mtf.move_to_front_encode(last_column)
    huffman_encoded, huffman_codes, padding_length = huff.huffman_encode(mtf_encoded)
    logging.debug("Processo di compressione dei dati completato.")
    return {
        'data': huffman_encoded,
        'padding_length': padding_length,
        'orig_ptr': orig_ptr,
        'symbols': symbols,
        'huffman_codes': huffman_codes
    }

def decompress_data(compressed_data, key):
    logging.debug("Inizio processo di decompressione dei dati.")
    huffman_encoded = compressed_data['data']
    padding_length = compressed_data['padding_length']
    orig_ptr = compressed_data['orig_ptr']
    symbols = compressed_data['symbols']
    huffman_codes = compressed_data['huffman_codes']

    huffman_decoded = huff.huffman_decode(huffman_encoded, huffman_codes, padding_length)
    mtf_decoded = mtf.move_to_front_decode(huffman_decoded, symbols)
    decompressed = sbwt.sbwt_decompress(mtf_decoded, orig_ptr, key)
    logging.debug("Processo di decompressione dei dati completato.")
    return decompressed

# Funzione per comprimere un singolo blocco (per parallelizzazione)
def compress_block(block_data, key):
    logging.debug("Compressione di un blocco.")
    compressed_data = compress_data(block_data, key)
    return compressed_data

# Funzione per decomprimere un singolo blocco (per parallelizzazione)
def decompress_block(compressed_data, key):
    logging.debug("Decompressione di un blocco.")
    decompressed_data = decompress_data(compressed_data, key)
    return decompressed_data

# Funzione per comprimere il file con suddivisione in blocchi e parallelizzazione
def compress_file(input_file, output_file, key):
    logging.info(f"Avvio compressione: {input_file} -> {output_file}")
    
    # Verifica se il file di input esiste
    if not os.path.isfile(input_file):
        logging.error(f"Il file di input '{input_file}' non esiste.")
        return
    
    # Calcola la dimensione del file di input
    input_size = os.path.getsize(input_file)
    logging.info(f"Dimensione del file di input: {input_size} byte.")
    
    start_time = time.perf_counter()  # Inizio della misurazione del tempo
    
    blocks = []
    with open(input_file, 'r', encoding='utf-8') as fin:
        block_number = 0
        while True:
            input_data = fin.read(BLOCK_SIZE)
            if not input_data:
                break
            block_number += 1
            blocks.append((block_number, input_data))
    
    logging.info(f"Totale blocchi da comprimere: {block_number}")
    
    compressed_blocks = {}
    
    # Calcolo del numero massimo di processi per utilizzare al massimo il 60% dei core
    total_cores = multiprocessing.cpu_count()
    num_workers = max(1, int(total_cores * 0.6))
    logging.info(f"Utilizzo di {num_workers} processi per la compressione parallela.")
    
    # Utilizzo di ProcessPoolExecutor per comprimere i blocchi in parallelo
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Mappare i blocchi al pool di processi
        futures = {executor.submit(compress_block, block_data, key): idx for idx, block_data in blocks}
        
        for future in as_completed(futures):
            idx = futures[future]
            try:
                compressed_data = future.result()
                compressed_blocks[idx] = compressed_data
            except Exception as e:
                logging.error(f"Errore nella compressione del blocco {idx}: {e}")
    
    # Scrivere i blocchi compressi in ordine
    with open(output_file, 'wb') as fout:
        for idx in range(1, block_number + 1):
            compressed_data = compressed_blocks.get(idx)
            if compressed_data is None:
                logging.error(f"Blocco {idx} mancante. Compressione incompleta.")
                continue
            
            # Cambiato da logging.info a logging.debug per evitare messaggi eccessivi
            logging.debug(f"Inizio scrittura del blocco {idx} compresso.")
            
            # Scrivi metadati per il blocco
            fout.write(compressed_data['padding_length'].to_bytes(1, byteorder='big'))
            fout.write(compressed_data['orig_ptr'].to_bytes(4, byteorder='big'))
            # Non salvare più custom_order
            
            mtf.save_symbols(fout, compressed_data['symbols'])
            huff.save_huffman_codes(fout, compressed_data['huffman_codes'])
            
            # Scrivi la lunghezza dei dati Huffman compressi
            data_length = len(compressed_data['data'])
            fout.write(data_length.to_bytes(4, byteorder='big'))  # 4 byte per data_length
            
            # Scrivi i dati Huffman compressi
            fout.write(compressed_data['data'])
            # Cambiato da logging.info a logging.debug per evitare messaggi eccessivi
            logging.debug(f"Scrittura del blocco {idx} completata.")
    
    end_time = time.perf_counter()  # Fine della misurazione del tempo
    duration = end_time - start_time
    logging.info(f"Compressione completata in {duration:.4f} secondi.")
    
    # Calcola la dimensione del file compresso
    compressed_size = os.path.getsize(output_file)
    logging.info(f"Dimensione del file compresso: {compressed_size} byte.")
    
    # Log della riduzione delle dimensioni
    if input_size > 0:
        if compressed_size < input_size:
            reduction = ((input_size - compressed_size) / input_size) * 100
            logging.info(f"Riduzione delle dimensioni: {reduction:.2f}%")
        else:
            logging.info("Compressione riuscima ma il file compresso è più pesante del file di input.")
    else:
        logging.warning("Il file di input è vuoto.")

# Funzione per decomprimere il file con suddivisione in blocchi e parallelizzazione
def decompress_file(input_file, output_file, key):
    logging.info(f"Avvio decompressione: {input_file} -> {output_file}")
    
    # Verifica se il file di input esiste
    if not os.path.isfile(input_file):
        logging.error(f"Il file di input '{input_file}' non esiste.")
        return
    
    # Calcola la dimensione del file compresso
    compressed_size = os.path.getsize(input_file)
    logging.info(f"Dimensione del file compresso: {compressed_size} byte.")
    
    start_time = time.perf_counter()  # Inizio della misurazione del tempo
    
    blocks = []
    with open(input_file, 'rb') as fin:
        while fin.tell() < compressed_size:
            block_number = len(blocks) + 1
            logging.debug(f"Inizio lettura del blocco {block_number}.")
            
            # Leggi metadati del blocco
            padding_length = int.from_bytes(fin.read(1), byteorder='big')
            orig_ptr = int.from_bytes(fin.read(4), byteorder='big')
            # Non caricare più custom_order
            
            symbols = mtf.load_symbols(fin)
            huffman_codes = huff.load_huffman_codes(fin)
            
            # Leggi la lunghezza dei dati Huffman compressi
            data_length = int.from_bytes(fin.read(4), byteorder='big')
            huffman_encoded = bytearray(fin.read(data_length))
            
            compressed_data = {
                'data': huffman_encoded,
                'padding_length': padding_length,
                'orig_ptr': orig_ptr,
                'symbols': symbols,
                'huffman_codes': huffman_codes
            }
            blocks.append((block_number, compressed_data))
    
    logging.info(f"Totale blocchi da decomprimere: {len(blocks)}")
    
    decompressed_blocks = {}
    
    # Calcolo del numero massimo di processi per utilizzare al massimo il 60% dei core
    total_cores = multiprocessing.cpu_count()
    num_workers = max(1, int(total_cores * 0.6))
    logging.info(f"Utilizzo di {num_workers} processi per la decompressione parallela.")
    
    # Utilizzo di ProcessPoolExecutor per decomprimere i blocchi in parallelo
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Mappare i blocchi al pool di processi
        futures = {executor.submit(decompress_block, block_data, key): idx for idx, block_data in blocks}
        
        for future in as_completed(futures):
            idx = futures[future]
            try:
                decompressed_data = future.result()
                decompressed_blocks[idx] = decompressed_data
            except Exception as e:
                logging.error(f"Errore nella decompressione del blocco {idx}: {e}")
    
    # Scrivere i blocchi decompressi in ordine
    with open(output_file, 'w', encoding='utf-8') as fout:
        for idx in range(1, len(blocks) + 1):
            decompressed_data = decompressed_blocks.get(idx)
            if decompressed_data is None:
                logging.error(f"Blocco {idx} mancante. Decompressione incompleta.")
                continue
            
            # Cambiato da logging.info a logging.debug per evitare messaggi eccessivi
            logging.debug(f"Inizio scrittura del blocco {idx} decompresso.")
            fout.write(decompressed_data)
            # Cambiato da logging.info a logging.debug per evitare messaggi eccessivi
            logging.debug(f"Scrittura del blocco {idx} completata.")
    
    end_time = time.perf_counter()  # Fine della misurazione del tempo
    duration = end_time - start_time
    logging.info(f"Decompressione completata in {duration:.4f} secondi.")
    
    # Calcola la dimensione del file di output
    output_size = os.path.getsize(output_file)
    logging.info(f"Dimensione del file di output: {output_size} byte.")
    
    # Log della crescita delle dimensioni
    if compressed_size > 0:
        growth = ((output_size - compressed_size) / compressed_size) * 100
        logging.info(f"Crescita delle dimensioni: {growth:.2f}%")
    else:
        logging.warning("Il file compresso è vuoto.")

# Funzione principale
def main():
    if len(sys.argv) < 5:
        print("Usage: python3 script.py <compress|decompress> <input_file> <output_file> <key>")
        sys.exit(1)

    operation = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    key = sys.argv[4]

    if operation == "compress":
        compress_file(input_file, output_file, key)
    elif operation == "decompress":
        decompress_file(input_file, output_file, key)
    else:
        print("Operazione non riconosciuta. Usa 'compress' o 'decompress'.")
        sys.exit(1)

if __name__ == "__main__":
    main()