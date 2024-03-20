"""
Этот скрипт выполняет две основные функции: извлекает координаты слов из предоставленных JSON данных и
вычисляет аффинную матрицу для преобразования координат между двумя изображениями.

Функция `extract_words_with_coordinates` принимает JSON-данные и список слов для поиска,
возвращая координаты слов в формате JSON. Она обрабатывает данные, чтобы идентифицировать и извлечь координаты слов,
которые затем можно использовать для выравнивания или других целей обработки изображений.

Функция `calculate_affine_matrix` принимает пути к двум JSON-файлам,
содержащим данные о словах и их координатах на двух изображениях, и список слов, которые нужно найти.
Затем она вычисляет аффинную матрицу, которая может быть использована для преобразования
координат точек с одного изображения на другое. Это особенно полезно при сопоставлении между шаблоном и целевым изображением,
чтобы определить степень схожести между ними.

По завершении, если матрица была успешно вычислена, скрипт выводит её, а также отображает статистику точек,
классифицированных как inliers, и среднюю ошибку преобразования.
Эта информация может быть использована для оценки точности и надежности преобразования.
"""


import json
import cv2
import numpy as np

def extract_words_with_coordinates(json_data, words_to_find):
    # Преобразуем слова для поиска в нижний регистр
    words_to_find_lower = set(word.lower() for word in words_to_find)

    # Словарь для хранения слов и их координат
    words_with_coords = {}
    duplicate_words = set()
    word_counts = {}



    # Извлечение слов и их координат из JSON данных
    for block in json_data['readResult']['blocks']:
        for line in block['lines']:
            for word_info in line['words']:
                word_text = word_info['text'].lower()
                #if word_text in
                bounding_polygon = word_info['boundingPolygon']
                #words_with_coords[word_text] = bounding_polygon

                # Добавляем слово в словарь, если оно есть в списке для поиска
                if word_text in words_to_find_lower:
                    words_with_coords[word_text] = bounding_polygon
                    word_counts[word_text] = word_counts.get(word_text, 0) + 1


                #if word_text in words_to_find_lower:
                #    if word_text in words_with_coords:
                #        duplicate_words.add(word_text)
                #    else:
                #        words_with_coords[word_text] = bounding_polygon

    # Исключаем дубликаты из результирующего словаря
    for word in duplicate_words:
        if word in words_with_coords:
            del words_with_coords[word]
            print(f"Слово '{word}' встречается несколько раз и было исключено.")

    return words_with_coords

def get_polygon_points(polygon):
    return [(point['x'], point['y']) for point in polygon]


# Загрузка JSON данных
#with open('results/result_page_1.json', 'r', encoding='utf-8') as file:
#with open('layout_reference.json', 'r', encoding='utf-8') as file:
#    json_data = json.load(file)

# Массив слов, которые нужно найти
words_to_find_standart = ['удостоверяю:',
                 'законодательства»',
                 'Всероссийская',
                 '145/1120-8',
                 'нижеподписавшиеся,',
                 'Уполномоченный',
                 '40810810938009426976',
                 'региональных',
                 'Специальный',
                 '(уполномоченных',
                 'представителей)']

# Получение слов и их координат
#words_coordinates = extract_words_with_coordinates(json_data, words_to_find)

# Вывод результатов
#for word, coords in words_coordinates.items():
    #if word in words_to_find:
#    print(f"Word: {word}, Coordinates: {coords}")



def calculate_affine_matrix(json_file1, json_file2='words_reference.json', words_to_find=words_to_find_standart):
    """Вычисляет матрицу аффинного преобразования между двумя страницами на основе слов. Тут мы вычисляем обратную матрицу."""


    with open(json_file1, 'r', encoding='utf-8') as file1, open(json_file2, 'r', encoding='utf-8') as file2:
        json_data1 = json.load(file1)
        json_data2 = json.load(file2)

    # Загрузка JSON данных из двух файлов
    #with open('results/result_page_2.json', 'r', encoding='utf-8') as file1, \
    #     open('results/result_page_6.json', 'r', encoding='utf-8') as file2:
    #    json_data1 = json.load(file1)
    #    json_data2 = json.load(file2)


    # Получение слов и их координат из каждого файла
    words_coordinates1 = extract_words_with_coordinates(json_data1, words_to_find)
    words_coordinates2 = extract_words_with_coordinates(json_data2, words_to_find)

    # Находим пересечение слов из обоих файлов
    common_words = set(words_coordinates1.keys()) & set(words_coordinates2.keys())

    if not common_words:
        print("Нет общих слов для вычисления преобразования.")
        return None

    # Вывод результатов
    #print("Слова, встречающиеся в обоих файлах:")
    #for word in common_words:
    #    print(word)


    # Подготовка данных для вычисления аффинного преобразования
    src_points = np.float32([point for word in common_words for point in get_polygon_points(words_coordinates1[word])])
    dst_points = np.float32([point for word in common_words for point in get_polygon_points(words_coordinates2[word])])

    # Вычисление аффинного преобразования
    #M, _ = cv2.estimateAffinePartial2D(src_points, dst_points)

    M, inliers = cv2.estimateAffinePartial2D(src_points, dst_points)
    if inliers is not None:
        inlier_ratio = np.sum(inliers) / len(inliers)
        print("Доля точек, классифицированных как inliers:", inlier_ratio)

    transformed_src_points = cv2.transform(np.array([src_points]), M)[0]
    errors = np.linalg.norm(transformed_src_points - dst_points, axis=1)
    mean_error = np.mean(errors)
    print("Средняя ошибка преобразования:", mean_error)


    if len(common_words) < 7:
        print(f"Найдено слов в обоих файлах: {len(common_words)} из {len(words_to_find)}")

    return M, mean_error

    # Вывод результата
    #print("Матрица аффинного преобразования:")
    #print(M)

if __name__ == "__main__":
    # Пример вызова функции
    M = calculate_affine_matrix('results/result_page_6.json')
    if M is not None:
        print("Матрица аффинного преобразования:")
        print(M)
