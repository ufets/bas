

from PIL import Image
import os

def int_to_bin(value, length=8):
    """Конвертирует целое число в бинарную строку фиксированной длины."""
    return bin(value)[2:].zfill(length)

def bin_to_int(binary):
    """Конвертирует бинарную строку в целое число."""
    return int(binary, 2)

def xor_encrypt(data, key):
    """Шифрование данных XOR."""
    key = key.encode()
    key_len = len(key)
    encrypted = bytearray()
    for i in range(len(data)):
        encrypted.append(data[i] ^ key[i % key_len])
    return encrypted

def xor_decrypt(data, key):
    """Расшифровка данных XOR."""
    return xor_encrypt(data, key)  # Шифрование и дешифрование идентичны

def embed_data_into_image(image_path, data_path, output_path, key):
    """Встраивание данных из файла в изображение методом LSB с предварительным XOR."""
    # Открываем изображение
    image = Image.open(image_path)
    pixels = image.load()

    # Читаем данные для встраивания
    with open(data_path, 'rb') as f:
        data = f.read()

    # Шифруем данные с помощью XOR
    encrypted_data = xor_encrypt(data, key)

    # Добавляем метку конца данных
    encrypted_data += b"<END>"

    # Преобразуем данные в бинарную строку
    binary_data = ''.join([int_to_bin(byte) for byte in encrypted_data])

    # Проверяем, поместятся ли данные в изображение
    width, height = image.size
    if len(binary_data) > width * height * 3:
        raise ValueError("Изображение слишком маленькое для встраивания данных.")

    # Встраивание данных
    data_index = 0
    for y in range(height):
        for x in range(width):
            if data_index >= len(binary_data):
                break

            r, g, b = pixels[x, y]

            # Заменяем младший бит красного канала на бит данных
            if data_index < len(binary_data):
                r = (r & ~1) | int(binary_data[data_index])
                data_index += 1

            # Заменяем младший бит зеленого канала на бит данных
            if data_index < len(binary_data):
                g = (g & ~1) | int(binary_data[data_index])
                data_index += 1

            # Заменяем младший бит синего канала на бит данных
            if data_index < len(binary_data):
                b = (b & ~1) | int(binary_data[data_index])
                data_index += 1

            pixels[x, y] = (r, g, b)

    # Сохраняем изображение с встроенными данными
    image.save(output_path)
    print(f"Данные успешно встроены в изображение: {output_path}")

def extract_data_from_image(image_path, output_path, key):
    """Извлечение данных из изображения с расшифровкой XOR."""
    # Открываем изображение
    image = Image.open(image_path)
    pixels = image.load()

    # Извлекаем бинарные данные из младших битов пикселей
    binary_data = ""
    width, height = image.size
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)

    # Преобразуем бинарные данные в байты
    extracted_bytes = bytearray()
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) < 8:
            continue
        extracted_bytes.append(bin_to_int(byte))

    # Определяем конец данных
    end_marker = b"<END>"
    end_index = extracted_bytes.find(end_marker)
    if end_index != -1:
        extracted_bytes = extracted_bytes[:end_index]

    # Расшифровываем данные с помощью XOR
    decrypted_data = xor_decrypt(extracted_bytes, key)

    # Сохраняем извлеченные данные в файл
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)
    print(f"Данные успешно извлечены в файл: {output_path}")

# Пример использования
if __name__ == "__main__":
    # Встраиваем данные
    embed_data_into_image("T1027.003_Tourist.png", "T1027.003_test.exe", "T1027.003_stego_image.png", "äô¹QÜ&s|ùWÎ~Ú¹_äb£7UÜ£#V¥wSQ}µG¥7SQW¸´ôsqAGmª¦Ø2³9m(ØáGb3wíYUWGÜ3wUY¾Êw")

    # Извлекаем данные
    extract_data_from_image("T1027.003_stego_image.png", "T1027.003_extracted_file.exe", "äô¹QÜ&s|ùWÎ~Ú¹_äb£7UÜ£#V¥wSQ}µG¥7SQW¸´ôsqAGmª¦Ø2³9m(ØáGb3wíYUWGÜ3wUY¾Êw")
