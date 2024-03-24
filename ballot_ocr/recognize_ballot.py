"""
Этот скрипт предназначен для автоматизированного распознавания и анализа избирательных бюллетеней.
Он поддерживает обработку изображений как из локального хранилища, так и по URL (Это недоделано) с помощью Azure Computer Vision.
Процесс включает выбор наилучшего шаблона для данного бюллетеня из предопределенной директории шаблонов,
анализ наличия отметок в бюллетене и классификацию бюллетеня по действительности.
Результатом выполнения является JSON-объект с детализацией отметок, информацией о действительности бюллетеня
и точности соответствия выбранного шаблона.
"""

import os
from glob import glob

from ballot_ocr.analize_squares import read_rectangles, analyze_rectangles
from ballot_ocr.ballot_vision import load_keywords_from_file, save_to_json
from ballot_ocr.find_keywords import calculate_affine_matrix
from ballot_ocr.pdf_vision import analyze_image, analyze_image_url


def get_json_filename(image_path, output_dir="ballots_jsons"):
    """
    Генерирует имя файла JSON на основе пути к изображению и директории для сохранения.

    :param image_path: Путь к исходному изображению.
    :param output_dir: Директория для сохранения файла JSON.
    :return: Полный путь к файлу JSON.
    """
    # Получаем имя файла без расширения
    base_name = os.path.basename(image_path)
    file_name_without_ext = os.path.splitext(base_name)[0]

    # Формируем имя файла JSON
    json_file_name = f"{file_name_without_ext}.json"

    # Формируем полный путь к файлу JSON
    json_file_path = os.path.join(output_dir, json_file_name)

    return json_file_path

def get_templates_info(templates_dir):
    """Возвращает список словарей с информацией о шаблонах."""
    templates_info = []
    ref_ballots = glob(os.path.join(templates_dir, "*_ref_ballot.json"))
    for ref_ballot_path in ref_ballots:
        prefix = os.path.basename(ref_ballot_path).split('_ref_ballot.json')[0]
        keywords_path = os.path.join(templates_dir, f"{prefix}_ref_ballot_words.json")
        rectangles_path = os.path.join(templates_dir, f"{prefix}_ref_rectangles.json")
        templates_info.append({
            "prefix": prefix,
            "keywords_path": keywords_path,
            "ref_json_path": ref_ballot_path,
            "rectangles_path": rectangles_path,
        })
    return templates_info

def recognize_ballot(image_path, verbose_mode=False, azure_ocr=True):
    """
    Распознает и анализирует бюллетень, используя шаблоны из указанной директории.

    :param image_path: Путь к изображению бюллетеня для анализа.
    :param verbose_mode: Если True, печатает дополнительную информацию в процессе выполнения.
    :param azure_ocr: Если True, использует Azure Computer Vision для распознавания текста на изображении.
    :return: JSON-объект с результатами анализа отметок, включая дополнительные поля 'invalid' и 'affinity_accuracy'.
    """
    #image_path = "test_ballots/due_photo_2024-03-15_16-15-04.jpg"
    #image_path = "test_ballots/new_ballot.jpg"
    templates_dir = "templates"

    templates_info = get_templates_info(templates_dir)

    best_error = float('inf')
    best_template_info = None
    best_affine_matrix = None

    for template_info in templates_info:
        keywords = load_keywords_from_file(template_info["keywords_path"])
        new_json_file = get_json_filename(image_path)
        print(f"json file path: {new_json_file}")
        #new_json_file = "ballots_jsons\\new_ballot.json"
        #new_json_file = 'tatar_ballot.json'
        #new_json_file = 'new_ballot.json'
        if azure_ocr:
            new_json_data = analyze_image(image_path)
            #new_json_data = analyze_image_url(image_path)
            save_to_json(new_json_data, new_json_file)
        M, mean_error = calculate_affine_matrix(template_info["ref_json_path"], new_json_file, keywords)

        if verbose_mode:
            print(f"Template {template_info['prefix']}: Mean Error = {mean_error}")

        if mean_error < best_error:
            best_error = mean_error
            best_template_info = template_info
            best_affine_matrix = M

    if best_template_info is not None:
        rectangles = read_rectangles(best_template_info["rectangles_path"])
        marks = analyze_rectangles(image_path, rectangles, best_affine_matrix, verbose_mode)

        # Подсчет количества True значений в отметках
        true_marks_count = sum(marks.values())

        # Добавление поля invalid в зависимости от количества True значений
        marks['invalid'] = true_marks_count != 1

        # Добавление поля affinity_accuracy
        marks['affinity_accuracy'] = best_error

        print(f"Using Template {best_template_info['prefix']} with Mean Error = {best_error}")
        #print(marks)
        return marks
    else:
        print("Could not find a suitable template.")
        return None

if __name__ == "__main__":

    # TODO: Сюда добавить кусок, скачивающий нужный файл из хранилища
    # Указываем адрес изучаемого бюллетеня:
    image_path = "test_ballots/new_ballot.jpg"
    #image_path = "http://s3.amazonaws.com/doc/2006-03-01/"

    #new_json_file = 'new_ballot.json'

    # Название директории для сохранения JSON файлов
    output_dir = "ballots_jsons"

    # Проверка существования директории и ее создание при необходимости
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Запускаем главную функцию распознавания бюллетеня. azure_ocr=True означает, что используется ресурс azure
    # Если azure_ocr = False, подразумевается, что есть результат распознавания в виде json и остается только распознать отметки
    marks = recognize_ballot(image_path, verbose_mode=False, azure_ocr=True)
    # Ответ содержит json с 6-ю полями: 4 отметки, флаг недействительного бюллетеня,
    # и точность подгонки аффинной матрицы (насколько нам подошел один из шаблонов бюллетеней)
    print(marks)
