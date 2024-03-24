"""
Скрипт - рудимент из другого проекта, поэтому тут может быть лишний функционал и не очень понятный нейминг.
Тем не менее он норм использует ажур для распознавания.
Этот скрипт используется для анализа изображений с помощью Microsoft Azure's Computer Vision API.
Основная функциональность включает в себя возможность обработки изображений как из локальных файлов, так и из URL-адресов,
включая поддержку облачного хранилища Amazon S3.

Функции в этом скрипте:

- `analyze_image`: Принимает путь к изображению на локальной машине и использует Azure's Computer Vision API
  для получения информации о содержимом изображения и извлечения текста.

- `analyze_image_url`: Позволяет анализировать изображения, расположенные по URL-адресу (например, на Amazon S3).
  Может использовать как прямые URL-адреса изображений, так и потоки данных изображений.

- `analyze_images`: Принимает список путей к изображениям и директорию для результатов,
  анализирует каждое изображение и сохраняет результаты в формате JSON.

- `pdf_OCR`: Принимает путь к PDF-файлу, конвертирует страницы PDF в JPEG изображения и применяет OCR к каждому изображению.
  Результаты OCR сохраняются в указанной директории.

Вспомогательные функции:

- `split_pdf_to_jpeg`: Конвертирует PDF-файл в серию JPEG-изображений, используя Ghostscript для обработки.

Конфигурационные параметры для подключения к Azure (такие как `endpoint` и `key`) предполагается устанавливать через внешний файл или переменные среды.

Скрипт включает в себя заглушки для применения фильтров к изображениям (закомментировано),
которые можно активировать для улучшения качества OCR.

Использование:

1. Установите значения `endpoint` и `key` в начале скрипта.
2. Запустите скрипт, указав путь к PDF-файлу.
3. Просмотрите результаты в директории `results`.

Обратите внимание, что скрипт требует правильной настройки для доступа к Azure и может потребовать дополнительные зависимости для работы с PDF.
"""


import json

import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures


#from apply_image_filter import apply_filters

# Поместите эти значения из вашего ресурса Azure
endpoint = 'azure_endpoint'
key = 'azure_key'


"""
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)  # INFO для общих сообщений, DEBUG для подробных сообщений

#handler = logging.StreamHandler(stream=sys.stdout)
handler = logging.FileHandler(filename='azure_vision.log')

logger.addHandler(handler)

formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
handler.setFormatter(formatter)
"""

# Функция для анализа изображения с использованием Computer Vision API
def analyze_image(image_path):

    # Создание клиента анализа изображений
    client = ImageAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key), logging_enable=False)

    with open(image_path, "rb") as image_stream:
        result = client.analyze(image_data=image_stream.read(), visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ])
        #result = client.analyze(image_data=image_stream.read(), visual_features=[VisualFeatures.READ])
        #client.anal
        return result.as_dict()

# Функция для анализа изображения с использованием Computer Vision API и Amazon S3
def analyze_image_url(image_path=None, use_local_file=True, s3_url=None):

    # Создание клиента анализа изображений для Azure
    client = ImageAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key), logging_enable=False)

    # Если нужно использовать локальный файл
    if use_local_file:
        with open(image_path, "rb") as image_stream:
            result = client.analyze(image_data=image_stream.read(), visual_features=[VisualFeatures.READ])
            return result.as_dict()

    # Если нужно использовать файл из S3
    elif s3_url:
        # Создание клиента S3
        #s3_client = boto3.client('s3')#, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        # Парсинг URL S3 для получения имени бакета и ключа объекта
        #bucket_name = s3_url.split('/')[2]
        #object_key = '/'.join(s3_url.split('/')[3:])

        # Получение файла из S3
        #s3_object = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        #image_stream = s3_object['Body'].read()

        # Анализ изображения из потока
        result = client.analyze(image_url=s3_url, visual_features=[VisualFeatures.READ])
        return result.as_dict()

# Функция для анализа изображений
def analyze_images(pages_paths, results_dir):
    for page_path in pages_paths:
        print(f"Analyzing: {page_path}")
        result_json = analyze_image(page_path)
        page_num = os.path.splitext(os.path.basename(page_path))[0]
        with open(os.path.join(results_dir, f'result_{page_num}.json'), 'w', encoding='utf-8') as f:
            json.dump(result_json, f, ensure_ascii=False, indent=4)
        #os.remove(page_path)  # Удаляем временный файл изображения
        #break # remove this after debug

# Путь к PDF файлу или URL
pdf_path = "КретоваЕН_нет_в_базе.pdf"  # Замените на путь к вашему PDF файлу
def pdf_OCR(pdf_path):

    temp_dir = "temp"
    results_dir = "results"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    filters = ["contrast", "sharpen", "black_white", "rotate_90"]

    # Разбиение PDF на страницы и их анализ
    if os.path.exists(pdf_path):
        # Получаем список всех файлов с расширением .png в директории
        #pages_paths = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith('.png') and os.path.isfile(os.path.join(temp_dir, f))]
        #pages_paths = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith('.jpg') and os.path.isfile(os.path.join(temp_dir, f))]
        ###print(pages_paths)
        #pages_paths = split_pdf(pdf_path, temp_dir)
        pages_paths = split_pdf_to_jpeg(pdf_path, temp_dir)
        ###filtered_pages = preprocess_images(pages_paths, filters, 'filtered')
        #analyze_images(filtered_pages, results_dir)
        analyze_images(pages_paths, results_dir)
        print("Analysis complete, results are in the 'results' directory.")
    else:
        print("PDF file does not exist.")

if __name__ == "__main__":
    # Укажите путь к вашему PDF файлу здесь
    pdf_file_path = "КретоваЕН_нет_в_базе.pdf"
    pdf_OCR(pdf_file_path)
