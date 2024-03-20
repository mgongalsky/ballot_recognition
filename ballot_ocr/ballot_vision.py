"""
Этот скрипт используется для анализа изображений бюллетеней и определения наличия отметок в заданных областях.
Для начала он загружает ключевые слова из JSON файла и использует Azure Computer Vision API для распознавания текста на изображении.
После получения данных от Azure, скрипт сохраняет результаты в новый JSON файл и вычисляет аффинное преобразование для сопоставления образца бюллетеня с шаблоном.
Если преобразование успешно, скрипт выводит матрицу преобразования и производит анализ наличия отметок, результаты которого возвращаются в виде JSON.
Необходимо убедиться, что сервис Azure Computer Vision настроен и ключи доступа прописаны в переменных окружения перед запуском скрипта.
"""


import json

from find_keywords import extract_words_with_coordinates, calculate_affine_matrix
from pdf_vision import analyze_image


def save_to_json(data, file_path):
    """
    Сохраняет данные в JSON файл.

    :param data: Данные для сохранения.
    :param file_path: Путь к файлу для сохранения.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_keywords_from_file(file_path):
    """
    Загружает список ключевых слов из JSON файла.

    :param file_path: Путь к JSON файлу с ключевыми словами.
    :return: Список ключевых слов.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        keywords = json.load(f)
    return keywords



def main():
    # Загружаем ключевые слова из файла
    keywords_file_path = 'ref_ballot_words.json'  # Укажите путь к файлу с ключевыми словами
    keywords = load_keywords_from_file(keywords_file_path)

    # Загрузка JSON данных для референсного бюллетеня
    #with open('ref_ballot.json', 'r', encoding='utf-8') as file:
    #    ref_json_data = json.load(file)

    ref_json_file = 'templates/temp2_ref_ballot.json'
    ref_json_file = 'ref_ballot.json'

    # Ваши настройки Azure и пути к файлам
    image_path = "new_ballot.jpg"  # Путь к изображению бюллетеня
    image_path = "test_ballots/due_photo_2024-03-15_16-15-04.jpg"  # Путь к изображению бюллетеня



    new_json_data = analyze_image(image_path)
    # Сохраняем результат работы Azure Vision в JSON файл
    new_json_file = 'new_ballot.json'
    new_json_file = 'templates/temp2_ref_ballot.json'
    save_to_json(new_json_data, new_json_file)

    M = calculate_affine_matrix(ref_json_file, new_json_file, keywords)
    if M is not None:
        print("Матрица аффинного преобразования:")
        print(M)
    else:
        print("Не удалось вычислить аффинную матрицу.")

    #keywords_coords = extract_words_with_coordinates(json_data, keywords)

    # Печать найденных слов и их координат
    #if keywords_coords:
    #    print("Найденные слова и их координаты:")
    #    for word, coords in keywords_coords.items():
    #        print(f"{word}: {coords}")
    #else:
    #    print("Ключевые слова не найдены.")

if __name__ == "__main__":
    main()
