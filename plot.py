import argparse
import sys
import os
import matplotlib.pyplot as plt

def generate_charts(stats_file, output_file):
    chars_processed = []
    compression_ratios = []
    trie_sizes = []
    times = []
    

    with open(stats_file, "r") as f:
        for line in f:
            if "Processed" in line:
                parts = line.split()
                try:
                    num_chars = int(parts[1])
                    compression_ratio = float(parts[5].strip(","))
                    elapsed_time = parts[7].strip(",s")
                    trie_size_kb = int(parts[10])/1024
                    chars_processed.append(num_chars)
                    compression_ratios.append(compression_ratio)
                    trie_sizes.append(trie_size_kb)
                    times.append(elapsed_time)

                except (IndexError, ValueError):
                   print(f"Skipping invalid statistics line: {line.strip()}")
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)  # 1 linha, 2 colunas, primeiro subplot
    plt.plot(chars_processed, compression_ratios)
    plt.xlabel("Caracteres processados")
    plt.ylabel("Taxa de compressão")
    plt.title("Taxa de compressão ao longo do tempo")
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(chars_processed, trie_sizes)
    plt.xlabel("Caracteres processados")
    plt.ylabel("Tamanho da trie (kilobytes)")
    plt.title("Tamanho da trie ao longo do tempo")
    plt.grid(True)

    plt.tight_layout() 
    plt.savefig(output_file)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Statistics reading and plotting script")
    parser.add_argument("input_file", help="Path to the statistics file")
    parser.add_argument("output_file", help="Path to the output .png file")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: Statistics file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    generate_charts(args.input_file, args.output_file)
    sys.exit(0)

if __name__ == "__main__":
    main()