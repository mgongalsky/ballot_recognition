"""
Этот скрипт анализирует изображения избирательных бюллетеней, определяя наличие отметок в предопределённых областях.
Использует алгоритмы компьютерного зрения для обработки изображений и выявления контуров внутри заданных прямоугольников.
Поддерживает коррекцию перспективы через аффинные преобразования для адаптации к изображениям, снятым под разными углами.
Результатом является словарь с булевыми значениями, отражающими наличие или отсутствие отметок в каждой анализируемой области.
"""


import cv2
import json
import numpy as np

from ballot_vision import load_keywords_from_file
from find_keywords import calculate_affine_matrix

# Путь к файлу с координатами прямоугольников
json_file_path = 'rectangles.json'

# Путь к исходному изображению
image_path = 'bulletin.jpg'  # Замените на путь к вашему изображению

# Чтение координат прямоугольников из JSON файла
def read_rectangles(json_file_path):
    with open(json_file_path, 'r') as f:
        rectangles = json.load(f)
    return rectangles

# Функция для вычисления косинуса угла между векторами v0->v1 и v0->v2
def angle_cos(p0, p1, p2):
    d1 = (p0 - p1).flatten()
    d2 = (p2 - p1).flatten()
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))

# Функция для вычисления угла в градусах
def calculate_angle(p0, p1, p2):
    angle = np.arccos(angle_cos(p0, p1, p2))
    return np.degrees(angle)

def contour_length(contour):
    """
    Вычисляет суммарную длину всех отрезков в контуре.
    """
    length = 0
    for i in range(len(contour)):
        p1 = contour[i][0]
        p2 = contour[(i + 1) % len(contour)][0]
        length += np.linalg.norm(p1 - p2)
    return length

def is_contour_close(contour1, contour2, max_distance=10):
    """
    Проверяет, все ли точки контура1 находятся в пределах max_distance от ближайшей точки контура2.
    """
    for point1 in contour1:
        # Создаем массив расстояний от point1 до всех точек в contour2
        distances = np.array([np.linalg.norm(point1 - point2) for point2 in contour2])
        # Если минимальное расстояние до любой точки contour2 больше max_distance, вернуть False
        if np.all(distances > max_distance):
            return False
    return True

def transform_points(points, affine_matrix):
    """
    Применяет аффинное преобразование к набору точек.

    :param points: Список точек (координат вершин прямоугольников).
    :param affine_matrix: Матрица аффинного преобразования 2x3.
    :return: Список преобразованных точек.
    """
    transformed_points = []
    for (x, y) in points:
        # Применяем аффинное преобразование к каждой точке
        vector = np.array([x, y, 1])
        transformed_point = np.dot(affine_matrix, vector)
        transformed_points.append((transformed_point[0], transformed_point[1]))
    return transformed_points


#def analyze_rectangles(image_path, rectangles, affine_matrix):
def analyze_rectangles(image_path, rectangles, affine_matrix=None, verbose_mode=False):
    """
    Функция analyze_rectangles предназначена для обнаружения и классификации контуров
    внутри заданных прямоугольных областей на изображении. Она выполняет следующие действия:
    1. Вырезает заданные прямоугольные области из изображения.
    2. Преобразует области в градации серого и применяет бинарную пороговую фильтрацию.
    3. Находит и фильтрует контуры по длине и форме, исключая нерелевантные.
    4. Классифицирует контуры на основе их геометрических характеристик.
    5. Выводит информацию о найденных и классифицированных контурах.
    """

    if affine_matrix is None:
        # Инициализация единичной матрицы, если другая не предоставлена
        affine_matrix = np.eye(2, 3, dtype=np.float32)


    img = cv2.imread(image_path)
    if img is None:
        print(f"Error loading image '{image_path}'. Check the file path.")
        exit(1)

    # Словарь для хранения результатов анализа
    marks_result = {}



    for i, rectangle in enumerate(rectangles, start=1):
        # Применяем аффинное преобразование к координатам каждого прямоугольника
        transformed_points = transform_points([(rectangle[0], rectangle[1]), (rectangle[2], rectangle[3])], affine_matrix)
        x1, y1 = transformed_points[0]
        x2, y2 = transformed_points[1]

        #height, width = img.shape[:2]
        #print(f"Width: {width}, Height: {height}")

        #print(f"x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")

    #for i, (x1, y1, x2, y2) in enumerate(rectangles, start=1):
        crop_img = img[int(y1):int(y2), int(x1):int(x2)]
        #img = cv2.imread(image_path)
        #if crop_img is None:
        #    print(f"Problem with crop_img. Check the file path.")
        #    exit(1)


        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        # Используем адаптивное пороговое значение
        #thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
         #                               cv2.THRESH_BINARY_INV, 11, 2)

        contours, _ = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        if verbose_mode:
            print(f"\nAnalyzing Rectangle {i}, found {len(contours)} contours.")
        #print(contours)

        if verbose_mode:
            # Рисуем все контуры на вырезанном изображении
            cv2.drawContours(crop_img, contours, -1, (0, 0, 255), 2)

        # Анализ наличия отметок
        mark_present = False


        valid_contours = []
        for cnt in contours:
            contour = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)

            # Исключаем контуры с одной вершиной
            if len(contour) <= 1:
                continue
            # Проверяем длину каждого контура
            if contour_length(contour) > 10:  # Порог длины отрезка
                valid_contours.append(contour)

        if verbose_mode:
            print(f"After validation, found {len(valid_contours)} contours.")
        #print(valid_contours)

        # Начинаем с копии всех действительных контуров
        filtered_contours = valid_contours[:]

        # Создаем список индексов контуров, которые нужно удалить
        contours_to_remove = []

        for k, contour1 in enumerate(valid_contours):
            for j, contour2 in enumerate(valid_contours):
                if k != j and j not in contours_to_remove and k not in contours_to_remove:
                    if is_contour_close(contour2, contour1, max_distance=10):
                        contours_to_remove.append(j)

        #print(contours_to_remove)
        # Удаляем контуры, индексы которых находятся в списке contours_to_remove
        filtered_contours = [cnt for k, cnt in enumerate(filtered_contours) if k not in contours_to_remove]

        if verbose_mode:
            print(f"After filtering, found {len(filtered_contours)} contours.")


        #print(filtered_contours)

        for cnt in filtered_contours:
            # Аппроксимируем контур с помощью многоугольника
            #contour = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            contour = cnt
            if verbose_mode:
                print(f"Contour vertices: {len(contour)}")

            if verbose_mode:
                # Распечатаем координаты вершин
                print("Contour coordinates:")
                for point in contour:
                    print(point[0])

            if len(contour) == 4:
                angles = []
                for j in range(4):
                    p0, p1, p2 = contour[j][0], contour[(j-1) % 4][0], contour[(j+1) % 4][0]
                    angle = calculate_angle(p1, p0, p2)  # Используем функцию для вычисления углов
                    angles.append(angle)

                #print(f"Angles of the contour: {angles}")
                # Проверяем, являются ли все углы близкими к 90 градусам
                if all(80 <= angle <= 100 for angle in angles):  # допустимый диапазон от 80 до 100 градусов
                    if verbose_mode:
                        print("Contour is likely a rectangle, empty.")
                else:
                    mark_present = True
                    if verbose_mode:
                        print("Contour is not a rectangle, mark detected.")
            else:
                if verbose_mode:
                    print("Contour is not a rectangle, mark detected.")
                mark_present = True


        marks_result[f"mark_{i}"] = mark_present

        if verbose_mode:
            # Выводим изображение с контурами
            cv2.imshow(f"Rectangle {i} with Contours", crop_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    return marks_result


if __name__ == '__main__':
    json_file_path = 'rectangles.json'  # Укажите путь к вашему JSON файлу
    image_path = 'new_ballot.jpg'  # Укажите путь к вашему изображению
    rectangles = read_rectangles(json_file_path)

    # Загружаем ключевые слова из файла
    keywords_file_path = 'ref_ballot_words.json'  # Укажите путь к файлу с ключевыми словами
    keywords = load_keywords_from_file(keywords_file_path)


    ref_json_file = 'ref_ballot.json'
    # Ваши настройки Azure и пути к файлам
    #image_path = "new_ballot.jpg"  # Путь к изображению бюллетеня



    #new_json_data = analyze_image(image_path)
    # Сохраняем результат работы Azure Vision в JSON файл
    new_json_file = 'new_ballot.json'
    #save_to_json(new_json_data, new_json_file)

    M = calculate_affine_matrix(ref_json_file, new_json_file, keywords)


    marks = analyze_rectangles(image_path, rectangles, M)
    print(marks)
