import os

def compress_rle(data):
    """Простой алгоритм сжатия RLE (Run-Length Encoding)."""
    compressed = []
    i = 0
    while i < len(data):
        count = 1
        while i + 1 < len(data) and data[i] == data[i + 1]:
            count += 1
            i += 1
        compressed.append((data[i], count))
        i += 1
    return compressed

def decompress_rle(compressed):
    """Декодирование RLE."""
    decompressed = []
    for char, count in compressed:
        decompressed.extend([char] * count)
    return bytes(decompressed)

def xor_encrypt(data, key):
    """Шифрование данных XOR."""
    key = key.encode()
    key_len = len(key)
    encrypted = bytearray()
    for i in range(len(data)):
        encrypted.append(data[i] ^ key[i % key_len])
    return encrypted

def xor_decrypt(data, key):
    """Расшифровка данных XOR (обратная операция такая же)."""
    return xor_encrypt(data, key)  # Шифрование и дешифрование идентичны

def save_archive(file_names, output_file, key):
    """Создание архива с сжатием и шифрованием."""
    archive = bytearray()
    for file_name in file_names:
        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                data = f.read()
                compressed = compress_rle(data)
                compressed_bytes = bytearray()
                for char, count in compressed:
                    compressed_bytes.append(char)
                    compressed_bytes.append(count)
                archive.extend(compressed_bytes)
                archive.append(0)  # Разделитель между файлами
        else:
            print(f"Файл {file_name} не найден.")

    encrypted_archive = xor_encrypt(archive, key)
    with open(output_file, 'wb') as f:
        f.write(encrypted_archive)
    print(f"Архив сохранен в файл: {output_file}")

def extract_archive(input_file, output_folder, key):
    """Извлечение данных из архива с расшифровкой и декомпрессией."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(input_file, 'rb') as f:
        encrypted_archive = f.read()

    archive = xor_decrypt(encrypted_archive, key)

    file_counter = 1
    current_file = bytearray()
    i = 0
    while i < len(archive):
        if archive[i] == 0:  # Разделитель между файлами
            if current_file:
                decompressed_data = decompress_rle(
                    [(current_file[j], current_file[j + 1]) for j in range(0, len(current_file), 2)]
                )
                output_file = os.path.join(output_folder, f'file_{file_counter}.bin')
                with open(output_file, 'wb') as out_f:
                    out_f.write(decompressed_data)
                print(f"Файл извлечен: {output_file}")
                file_counter += 1
                current_file = bytearray()
            i += 1
        else:
            current_file.append(archive[i])
            i += 1

# Пример использования
if __name__ == "__main__":
    key = "secretkey"

    # Создание архива
    file_list = ["file1.txt", "file2.txt"]  # Список файлов для архивации
    save_archive(file_list, "archive.bin", key)

    # Извлечение архива
    extract_archive("archive.bin", "output_files", key)
