# Модуль обнаружения характеристических точек

Этот модуль предоставляет возможности обнаружения признаков с помощью различных детекторов, таких как ORB, SIFT и SuperPoint.

## Структура модуля

Структура проекта выглядит следующим образом:

```
feature_detection
        ├── __init__.py
        ├──── orb_sift_detectors.py
        ├──── superpoint_detectors.py
        └── README.md
```

- `__init__.py`: Этот файл импортирует необходимые функции, чтобы сделать их доступными с уровня модуля.
- `orb_sift_detectors.py`: Реализует извлечение ключевых точек и дескрипторов с помощью детекторов ORB и SIFT.
- `superpoint_detectors.py`: Реализует извлечение ключевых точек и дескрипторов с помощью модели SuperPoint.

## Зависимости

Для запуска скриптов обнаружения признаков необходимы следующие зависимости:

- `opencv-python`: Для обработки изображений и обнаружения ключевых точек.
- `matplotlib`: Для визуализации обнаруженных ключевых точек.
- `torch`: Для использования модели SuperPoint с PyTorch.
- `transformers`: Для загрузки и обработки изображений с помощью модели SuperPoint.
- `pillow`: Для работы с изображениями.

Все необходимые зависимости и инструкции по сборке определены в файле `pyproject.toml`, который находится в корне репозитория. Способ установки описан в [Установка](../../../README.md#%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0)

## Запуск детекторов

### Детектор ORB/SIFT

Чтобы запустить скрипт `orb-sift-detector` из командной строки:

```bash
orb-sift-detector --detector [ORB/SIFT] --image1 <путь_к_изображению1> --image2 <путь_к_изображению2>
```

#### Аргументы:

- `--detector`: Выбор между `ORB` (по умолчанию) или `SIFT`.
- `--image1`: Путь к первому изображению (по умолчанию: `notebooks/feature_detection/data/cam2_1.jpg`).
- `--image2`: Путь ко второму изображению (по умолчанию: `notebooks/feature_detection/data/cam1_1.jpg`).

Например, чтобы запустить детектор ORB на двух изображениях:

```bash
orb-sift-detector --detector ORB --image1 ./path/to/image1.jpg --image2 ./path/to/image2.jpg
```

### Детектор SuperPoint

Детектор SuperPoint использует предобученную модель `magic-leap-community/superpoint` для обнаружения ключевых точек и дескрипторов.

Чтобы запустить скрипт `superpoint-detector` из командной строки:

```bash
superpoint-detector --image1 <путь_к_изображению1> --image2 <путь_к_изображению2>
```

#### Аргументы:

- `--image1`: Путь к первому изображению (по умолчанию: `notebooks/feature_detection/data/cam2_1.jpg`).
- `--image2`: Путь ко второму изображению (по умолчанию: `notebooks/feature_detection/data/cam1_1.jpg`).

Например, чтобы запустить детектор SuperPoint на двух изображениях:

```bash
superpoint-detector --image1 ./path/to/image1.jpg --image2 ./path/to/image2.jpg
```

## Пайплайн работы с характеристическими точками

[Jupyter блокнот](../../../notebooks/feature_detection/feature_detection.ipynb) с подробным описанием методов обнаружения характеристических точек на основе ORB, SIFT и SuperPoint с их сравнением.
