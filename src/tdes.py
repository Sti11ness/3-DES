import binascii
import os
import multiprocessing

def encrypt_block(block, key1, key2, key3):
    des1 = DES(key1)
    des2 = DES(key2)
    des3 = DES(key3)

    block = des1.encrypt_block(block)
    block = des2.decrypt_block(block)
    block = des3.encrypt_block(block)
    return block

def decrypt_block(block, key1, key2, key3):
    des1 = DES(key1)
    des2 = DES(key2)
    des3 = DES(key3)

    block = des3.decrypt_block(block)
    block = des2.encrypt_block(block)
    block = des1.decrypt_block(block)
    return block

# Начальная перестановка IP
IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17,  9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

# Конечная перестановка FP
FP = [
    40,  8, 48, 16, 56, 24, 64, 32,
    39,  7, 47, 15, 55, 23, 63, 31,
    38,  6, 46, 14, 54, 22, 62, 30,
    37,  5, 45, 13, 53, 21, 61, 29,
    36,  4, 44, 12, 52, 20, 60, 28,
    35,  3, 43, 11, 51, 19, 59, 27,
    34,  2, 42, 10, 50, 18, 58, 26,
    33,  1, 41,  9, 49, 17, 57, 25
]

# Таблица расширения E
E = [
    32,  1,  2,  3,  4,  5,
     4,  5,  6,  7,  8,  9,
     8,  9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32,  1
]

# S-блоки (8 блоков по 4 строки и 16 столбцов)
S_BOX = [
    # S1
    [
        [14, 4,13, 1, 2,15,11, 8, 3,10, 6,12, 5, 9, 0, 7],
        [ 0,15, 7, 4,14, 2,13, 1,10, 6,12,11, 9, 5, 3, 8],
        [ 4, 1,14, 8,13, 6, 2,11,15,12, 9, 7, 3,10, 5, 0],
        [15,12, 8, 2, 4, 9, 1, 7, 5,11, 3,14,10, 0, 6,13]
    ],
    # S2
    [
        [15, 1, 8,14, 6,11, 3, 4, 9, 7, 2,13,12, 0, 5,10],
        [ 3,13, 4, 7,15, 2, 8,14,12, 0, 1,10, 6, 9,11, 5],
        [ 0,14, 7,11,10, 4,13, 1, 5, 8,12, 6, 9, 3, 2,15],
        [13, 8,10, 1, 3,15, 4, 2,11, 6, 7,12, 0, 5,14, 9]
    ],
    # S3
    [
        [10, 0, 9,14, 6, 3,15, 5, 1,13,12, 7,11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6,10, 2, 8, 5,14,12,11,15, 1],
        [13, 6, 4, 9, 8,15, 3, 0,11, 1, 2,12, 5,10,14, 7],
        [ 1,10,13, 0, 6, 9, 8, 7, 4,15,14, 3,11, 5, 2,12]
    ],
    # S4
    [
        [ 7,13,14, 3, 0, 6, 9,10, 1, 2, 8, 5,11,12, 4,15],
        [13, 8,11, 5, 6,15, 0, 3, 4, 7, 2,12, 1,10,14, 9],
        [10, 6, 9, 0,12,11, 7,13,15, 1, 3,14, 5, 2, 8, 4],
        [ 3,15, 0, 6,10, 1,13, 8, 9, 4, 5,11,12, 7, 2,14]
    ],
    # S5
    [
        [ 2,12, 4, 1, 7,10,11, 6, 8, 5, 3,15,13, 0,14, 9],
        [14,11, 2,12, 4, 7,13, 1, 5, 0,15,10, 3, 9, 8, 6],
        [ 4, 2, 1,11,10,13, 7, 8,15, 9,12, 5, 6, 3, 0,14],
        [11, 8,12, 7, 1,14, 2,13, 6,15, 0, 9,10, 4, 5, 3]
    ],
    # S6
    [
        [12, 1,10,15, 9, 2, 6, 8, 0,13, 3, 4,14, 7, 5,11],
        [10,15, 4, 2, 7,12, 9, 5, 6, 1,13,14, 0,11, 3, 8],
        [ 9,14,15, 5, 2, 8,12, 3, 7, 0, 4,10, 1,13,11, 6],
        [ 4, 3, 2,12, 9, 5,15,10,11,14, 1, 7, 6, 0, 8,13]
    ],
    # S7
    [
        [ 4,11, 2,14,15, 0, 8,13, 3,12, 9, 7, 5,10, 6, 1],
        [13, 0,11, 7, 4, 9, 1,10,14, 3, 5,12, 2,15, 8, 6],
        [ 1, 4,11,13,12, 3, 7,14,10,15, 6, 8, 0, 5, 9, 2],
        [ 6,11,13, 8, 1, 4,10, 7, 9, 5, 0,15,14, 2, 3,12]
    ],
    # S8
    [
        [13, 2, 8, 4, 6,15,11, 1,10, 9, 3,14, 5, 0,12, 7],
        [ 1,15,13, 8,10, 3, 7, 4,12, 5, 6,11, 0,14, 9, 2],
        [ 7,11, 4, 1, 9,12,14, 2, 0, 6,10,13,15, 3, 5, 8],
        [ 2, 1,14, 7, 4,10, 8,13,15,12, 9, 0, 3, 5, 6,11]
    ]
]

# Функция перестановки P
P = [
    16,  7, 20, 21,
    29, 12, 28, 17,
     1, 15, 23, 26,
     5, 18, 31, 10,
     2,  8, 24, 14,
    32, 27,  3,  9,
    19, 13, 30,  6,
    22, 11,  4, 25
]

# Таблица PC-1 для генерации ключей
PC_1 = [
    57, 49, 41, 33, 25, 17,  9,
     1, 58, 50, 42, 34, 26, 18,
    10,  2, 59, 51, 43, 35, 27,
    19, 11,  3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
     7, 62, 54, 46, 38, 30, 22,
    14,  6, 61, 53, 45, 37, 29,
    21, 13,  5, 28, 20, 12,  4
]

# Таблица PC-2 для генерации ключей
PC_2 = [
    14, 17, 11, 24,  1,  5,
     3, 28, 15,  6, 21, 10,
    23, 19, 12,  4, 26,  8,
    16,  7, 27, 20, 13,  2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

# Количество сдвигов при генерации ключей
SHIFT = [
    1, 1, 2, 2,
    2, 2, 2, 2,
    1, 2, 2, 2,
    2, 2, 2, 1
]

def permute(block, table):
    return [block[x - 1] for x in table]

def xor(t1, t2):
    return [a ^ b for a, b in zip(t1, t2)]

def shift_left(block, n):
    return block[n:] + block[:n]

def sbox_substitution(block):
    result = []
    for i in range(8):
        chunk = block[i*6:(i+1)*6]
        row = (chunk[0] << 1) + chunk[5]
        col = (chunk[1] << 3) + (chunk[2] << 2) + (chunk[3] << 1) + chunk[4]
        val = S_BOX[i][row][col]
        bin_val = [int(x) for x in format(val, '04b')]
        result.extend(bin_val)
    return result

def f_function(r_block, subkey):
    expanded_block = permute(r_block, E)
    xored = xor(expanded_block, subkey)
    sbox_output = sbox_substitution(xored)
    f_result = permute(sbox_output, P)
    return f_result

class DES:
    def __init__(self, key):
        self.key = key
        self.subkeys = self.generate_subkeys(key)

    def generate_subkeys(self, key):
        key_bits = self.string_to_bit_array(key)
        key_permuted = permute(key_bits, PC_1)
        left, right = key_permuted[:28], key_permuted[28:]
        subkeys = []
        for shift in SHIFT:
            left = shift_left(left, shift)
            right = shift_left(right, shift)
            combined = left + right
            subkey = permute(combined, PC_2)
            subkeys.append(subkey)
        return subkeys

    def string_to_bit_array(self, data):
        array = []
        for byte in data:
            binval = bin(byte)[2:].rjust(8, '0')
            array.extend([int(x) for x in binval])
        return array

    def bit_array_to_bytes(self, array):
        res = bytes([int(''.join([str(bit) for bit in array[i:i+8]]), 2)
                     for i in range(0, len(array), 8)])
        return res

    def encrypt_block(self, block):
        block_bits = self.string_to_bit_array(block)
        block_bits = permute(block_bits, IP)
        left, right = block_bits[:32], block_bits[32:]
        for subkey in self.subkeys:
            temp = right.copy()
            right = xor(left, f_function(right, subkey))
            left = temp
        combined = right + left
        ciphertext_bits = permute(combined, FP)
        ciphertext = self.bit_array_to_bytes(ciphertext_bits)
        return ciphertext

    def decrypt_block(self, block):
        block_bits = self.string_to_bit_array(block)
        block_bits = permute(block_bits, IP)
        left, right = block_bits[:32], block_bits[32:]
        for subkey in reversed(self.subkeys):
            temp = right.copy()
            right = xor(left, f_function(right, subkey))
            left = temp
        combined = right + left
        plaintext_bits = permute(combined, FP)
        plaintext = self.bit_array_to_bytes(plaintext_bits)
        return plaintext

class TDES:
    def __init__(self, key1, key2, key3):
        self.key1 = key1
        self.key2 = key2
        self.key3 = key3

    @staticmethod
    def encode_data(data):
        return data.encode('utf-8')

    @staticmethod
    def decode_data(data):
        return data.decode('utf-8')

    def encrypt(self, data):
        # Выполняем заполнение данных
        data = pad_data(data)
        blocks = [data[i:i + 8] for i in range(0, len(data), 8)]

        # Используем multiprocessing для ускорения
        with multiprocessing.Pool() as pool:
            encrypted_blocks = pool.starmap(encrypt_block, [(block, self.key1, self.key2, self.key3) for block in blocks])

        return b''.join(encrypted_blocks)

    def decrypt(self, data):
        blocks = [data[i:i + 8] for i in range(0, len(data), 8)]

        # Используем multiprocessing для ускорения
        with multiprocessing.Pool() as pool:
            decrypted_blocks = pool.starmap(decrypt_block, [(block, self.key1, self.key2, self.key3) for block in blocks])

        decrypted_data = b''.join(decrypted_blocks)
        return unpad_data(decrypted_data)

def pad_data(data):
    pad_len = 8 - (len(data) % 8)
    padding = bytes([pad_len] * pad_len)
    return data + padding

def unpad_data(data):
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 8:
        raise ValueError("Invalid padding length.")
    # Проверяем, что все байты заполнения имеют правильное значение
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Invalid padding bytes.")
    return data[:-pad_len]

def main():
    # Ключи должны быть 8 байт (64 бита) для DES
    key1 = b'12345678'  # Пример ключа
    key2 = bytes([0xFF] * 8)
    key3 = key2  # Второй и третий ключи одинаковы

    tdes = TDES(key1, key2, key3)

    # Проверяем наличие папки data и файлов in.txt, out.txt
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    input_file = os.path.join(data_dir, 'in.txt')
    output_file = os.path.join(data_dir, 'out.txt')

    # Чтение и обработка данных поблочно
    if os.path.exists(input_file):
        with open(input_file, 'r', encoding='utf-8') as fin:
            with open(output_file, 'w', encoding='utf-8') as fout:
                # Читаем данные из входного файла
                plaintext = fin.read()

                # Кодируем данные
                data = encode_data(plaintext)

                # Шифрование
                ciphertext = tdes.encrypt(data)

                # Записываем шифротекст в hex формате
                fout.write('Шифротекст (hex):\n')
                fout.write(binascii.hexlify(ciphertext).decode('utf-8') + '\n\n')

                # Расшифровка
                decrypted_data = tdes.decrypt(ciphertext)
                decrypted_text = decode_data(decrypted_data)

                # Записываем расшифрованный текст
                fout.write('Расшифрованный текст:\n')
                fout.write(decrypted_text + '\n')
    else:
        raise FileNotFoundError(f"Input file '{input_file}' not found.")

if __name__ == '__main__':
    main()
