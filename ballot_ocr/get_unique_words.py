"""
Этот скрипт обрабатывает JSON файл, извлекает из него уникальные слова длиной 4 символа и более,
которые встречаются в тексте ровно один раз, и сохраняет их в отдельный JSON файл.
Это может быть полезно для анализа текстовых данных и выделения редких терминов или ключевых слов.

Входной JSON предполагается быть результатом OCR и содержит структурированную информацию о распознанных словах и их расположении.
Скрипт может быть использован для подготовки данных для дальнейшего анализа или обработки,
например, для создания списка ключевых слов для поиска или сравнения документов.

Для запуска скрипта замените переменные `json_file_path` и `output_file_path` на пути к вашим файлам.
"""

import json

def extract_and_save_unique_words(json_file_path, output_file_path):
    """
    Извлекает слова длиной 4 символа и более, которые встречаются ровно один раз в JSON файле,
    и сохраняет их в другой JSON файл.

    :param json_file_path: Путь к исходному JSON файлу.
    :param output_file_path: Путь к выходному JSON файлу, куда будут сохранены уникальные слова.
    """
    word_counts = {}

    with open(json_file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

        for block in json_data.get('readResult', {}).get('blocks', []):
            for line in block.get('lines', []):
                for word_info in line.get('words', []):
                    word_text = word_info.get('text', '').lower()

                    # Подсчет вхождений каждого слова
                    word_counts[word_text] = word_counts.get(word_text, 0) + 1

    # Фильтрация слов, встречающихся ровно один раз и имеющих 4 или более символов
    unique_words = [word for word, count in word_counts.items() if count == 1 and len(word) >= 4]

    # Сохранение уникальных слов в JSON файл
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(unique_words, output_file, ensure_ascii=False, indent=4)

    print(f"Уникальные слова длиной 4 символа и более были успешно сохранены в файл '{output_file_path}'.")

if __name__ == "__main__":
    json_file_path = 'ref_ballot.json'  # Укажите путь к вашему JSON файлу
    output_file_path = 'ref_ballot_words.json'  # Путь к выходному файлу для уникальных слов
    #json_file_path = 'templates/temp2_ref_ballot.json'  # Укажите путь к вашему JSON файлу
    #output_file_path = 'templates/temp2_ref_ballot_words.json'  # Путь к выходному файлу для уникальных слов

    extract_and_save_unique_words(json_file_path, output_file_path)
