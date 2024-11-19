import argparse
import sys
import os
import time
import struct
from model.lzw import Lzw
import pympler.asizeof

def get_text_size_in_bits(text):
    return len(text) * 8

def get_compressed_size_in_bits(compressed_codes):
    return sum(len(code) for code in compressed_codes)

def print_partial_statistics(partial_stats_list):
    with open("test/statistics.txt", "w") as f:
        for stat_line in partial_stats_list:
            f.write(stat_line + "\n")

def print_statistics(input_text, compressed_codes, elapsed_time, trie_size, trie_elements):
    with open("test/statistics.txt", "a") as f:
        f.write("\n")
        original_size = get_text_size_in_bits(input_text)
        compressed_size = get_compressed_size_in_bits(compressed_codes)

        compression_ratio = original_size / compressed_size

        f.write(f"Original Size: {original_size} bits ({original_size/8: .2f})bytes, ({original_size/8096: .2f})kb, ({original_size/8096/1024: .2f})mb\n")
        f.write(f"Compressed Size: {compressed_size} bits ({compressed_size/8: .2f})bytes, ({compressed_size/8096: .2f})kb, ({original_size/8096/1024: .2f})mb\n")
        f.write(f"Compression Ratio: {compression_ratio:.2f}\n")
        f.write(f"Trie Size (Memory): {trie_size} bytes\n")
        f.write(f"Trie Elements: {trie_elements}\n")
        f.write(f"Elapsed Time: {elapsed_time:.4f} seconds")

def main():
    parser = argparse.ArgumentParser(description="LZW Compression and Decompression with Trie")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("output_file", help="Path to the output file")
    parser.add_argument("-m", "--max_bits", type=int, default=12, help="Maximum number of bits (default: 12)")
    parser.add_argument("-d", "--dynamic", action="store_true", help="Use dynamic bit length (default: fixed)")
    parser.add_argument("-t", "--test", action="store_true", help="Enable testing mode (collect statistics)")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    start_time = time.time()
    lzw = Lzw()

    compressed_codes = []  
    if args.test: # Modo de teste
        if os.path.exists("test/statistics.txt"):
            os.remove("test/statistics.txt")

        compressed_codes = lzw.lzw_compress_with_trie(input_text, args.max_bits, args.dynamic)
        end_time = time.time()

        partial_stats_list = []
        for i, char in enumerate(input_text):
            if i % 20 != 0:
                continue

            intermediate_codes = lzw.lzw_compress_with_trie(input_text[:i+1], args.max_bits, args.dynamic) # Corta a string para cada passo
            compressed_codes = intermediate_codes
            current_time = time.time()
            elapsed_time = current_time - start_time

            original_size = get_text_size_in_bits(input_text[:i+1])
            compressed_size = get_compressed_size_in_bits(compressed_codes)

            trie_size = pympler.asizeof.asizeof(lzw.getTrie())
            trie_elements = len(lzw.getTrie().walk_trie())

            compression_ratio = original_size / compressed_size
            stat_str = f"Processed {i+1} characters. Compression ratio: {compression_ratio:.2f}, Time: {elapsed_time:.4f}s, Trie Size: {trie_size} bytes, Trie Elements: {trie_elements}"

            partial_stats_list.append(stat_str) 

        print_partial_statistics(partial_stats_list) 

        trie_size = pympler.asizeof.asizeof(lzw.getTrie())
        trie_elements = len(lzw.getTrie().walk_trie())

        decompressed_text = lzw.lzw_decompress_with_trie(compressed_codes, args.max_bits, args.dynamic)
        elapsed_time = end_time - start_time

        print_statistics(input_text, compressed_codes, elapsed_time, trie_size, trie_elements)
        with open(args.output_file, "wb") as f:
            for code in compressed_codes:
                packed_code = struct.pack(">H", int(code, 2))
                f.write(packed_code)

        sys.exit(0)

    dynamic = False
    if args.dynamic: #Compressão dinâmica
        dynamic = True

    compressed_codes = lzw.lzw_compress_with_trie(input_text, args.max_bits, dynamic=dynamic)
    decompressed_text = lzw.lzw_decompress_with_trie(compressed_codes, args.max_bits, dynamic=dynamic)

    with open(args.output_file, "wb") as f:
            for code in compressed_codes:
                packed_code = struct.pack(">H", int(code, 2))
                f.write(packed_code)

if __name__ == "__main__":
    main()