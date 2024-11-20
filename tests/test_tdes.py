import os
import sys
import unittest
import multiprocessing
# Добавляем путь к директории src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from tdes import DES, TDES

class TestDES(unittest.TestCase):
    def test_des_encrypt(self):
        key = bytes.fromhex('133457799BBCDFF1')
        plaintext = bytes.fromhex('0123456789ABCDEF')
        expected_ciphertext = bytes.fromhex('85E813540F0AB405')

        des = DES(key)
        ciphertext = des.encrypt_block(plaintext)

        self.assertEqual(ciphertext, expected_ciphertext)

    def test_des_decrypt(self):
        key = bytes.fromhex('133457799BBCDFF1')
        ciphertext = bytes.fromhex('85E813540F0AB405')
        expected_plaintext = bytes.fromhex('0123456789ABCDEF')

        des = DES(key)
        plaintext = des.decrypt_block(ciphertext)

        self.assertEqual(plaintext, expected_plaintext)

    def test_large_file(self):
        key1 = b'12345678'
        key2 = bytes([0xFF] * 8)
        key3 = key2

        tdes = TDES(key1, key2, key3)
        # Генерируем большой текст, содержащий различные символы
        plaintext = 'Тестовое сообщение\n' * 5000  # Повторяем строку 5000 раз
        data = tdes.encode_data(plaintext)

        # Шифрование с использованием multiprocessing
        ciphertext = tdes.encrypt(data)

        # Расшифровка с использованием multiprocessing
        decrypted_data = tdes.decrypt(ciphertext)
        decrypted_text = tdes.decode_data(decrypted_data)

        self.assertEqual(plaintext, decrypted_text)

if __name__ == '__main__':
    # На Windows multiprocessing требует защиту вызова
    multiprocessing.freeze_support()
    unittest.main()