import binascii
from model.trie import Trie

class Lzw:
    __trie = Trie()

    def bits_to_text(self, bits):
        if len(bits) % 8 != 0:
            raise ValueError("The bit string length must be a multiple of 8.")

        bytes_list = [bits[i:i+8] for i in range(0, len(bits), 8)]

        text = ''.join([chr(int(byte, 2)) for byte in bytes_list])

        return text

    def text_to_bits(self, text):
        if not isinstance(text, str):
            raise ValueError("Input must be a string.")

        bits = ''.join(format(ord(char), '08b') for char in text)
        return bits

    def number_to_bits(self, number, max_bits):
        if not isinstance(number, int):
            raise ValueError("Input must be an integer.")

        if number >= 2 ** max_bits or number < 0: # Chega se o numero  de bits é suficiente
            raise ValueError(f"The number {number} cannot be represented with {max_bits} bits.")

        binary_representation = format(number, f'0{max_bits}b')

        return binary_representation

    def number_to_bits(self, number, bit_length):
        """
        Converte um número inteiro para uma representação binária com comprimento fixo.
        """
        return format(number, f'0{bit_length}b')

    def lzw_compress_with_trie(self, text, max_bits=12, dynamic=False):
        self.__trie = Trie()

        # Inicializar com os caracteres ASCII
        for i in range(256):
            self.__trie.insert(chr(i))
            self.__trie.root.children[chr(i)].code = i

        current_string = ""
        code_value = 256
        max_code = (1 << max_bits) - 1
        compressed_codes = []

        current_bit_length = max_bits
        if dynamic:
            current_bit_length = 8

        for char in text:
            combined_string = current_string + char
            found_node = self.__trie.find_prefix(combined_string)

            if found_node:
                current_string = combined_string
            else:
                # Obter o código da sequência atual
                node = self.__trie.root
                for c in current_string:
                    node = node.children[c]
                binary_code = self.number_to_bits(node.code, current_bit_length)
                compressed_codes.append(binary_code)

                # Inserir o novo prefixo
                if code_value <= max_code:
                    self.__trie.insert(combined_string)

                    # Atualiza o código do prefixo novo
                    if self.__trie.root.children[combined_string[0]].code is None:
                        self.__trie.update_code(combined_string, code_value)
                    code_value += 1

                # Ajuste dinâmico de bits, se necessário
                if dynamic and code_value > (1 << current_bit_length) and current_bit_length < max_bits:
                    current_bit_length += 1

                current_string = char

        # Adiciona o código para a última sequência
        if current_string:
            node = self.__trie.root
            for c in current_string:
                node = node.children[c]
            binary_code = self.number_to_bits(node.code, current_bit_length)
            compressed_codes.append(binary_code)

        return compressed_codes

    def lzw_decompress_with_trie(self, binary_codes, max_bits=12, dynamic=False):
        # Inicializar a Trie com caracteres ASCII
        self.__trie = Trie()
        for i in range(256):
            self.__trie.insert(chr(i))
            self.__trie.root.children[chr(i)].code = i

        code_value = 256
        max_code = (1 << max_bits) - 1

        # Início com 8 bits para caracteres ASCII
        current_bit_length = max_bits
        if dynamic:
            current_bit_length = 8

        # Converter o primeiro código binário para inteiro
        previous_code = int(binary_codes[0], 2)
        previous_string = self.__trie.find_prefix_by_code(previous_code)
        decompressed_text = previous_string

        for binary_code in binary_codes[1:]:
            current_code = int(binary_code, 2)
            if self.__trie.find_prefix_by_code(current_code):
                current_string = self.__trie.find_prefix_by_code(current_code)
            else:
                # Caso especial: o código atual não está na Trie
                current_string = previous_string + previous_string[0]

            decompressed_text += current_string

            # Adicionar nova sequência à Trie
            if code_value <= max_code:
                new_sequence = previous_string + current_string[0]
                self.__trie.insert(new_sequence)
                code_value += 1

            # Ajustar o comprimento dos bits dinamicamente, se necessário
            if dynamic and code_value > (1 << current_bit_length) and current_bit_length < max_bits:
                current_bit_length += 1

            previous_string = current_string

        return decompressed_text
    
    def getTrie(self):
        return self.__trie