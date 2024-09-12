# Интерфейс

## Обзор

Эта часть проекта представляет собою пользовательский интерфейс, в котором пользователь вводит данные о камере, расстоянии между камерами, загружает либо две фотографии детали с разных ракурсов, либо полноценную 3д модель. После нажатия на кнопку Upload and Process на данном этапе будут выставляться параметры камеры и выводиться результат (на данный момент это фиксированная строка, как только ML часть будет сделана, результатом будет являться расчет какого-либо расстояния у детали).

## Запуск

Для запуска необходимо предварительно скачать FastAPI, uvicorn перейти в корень проекта (MyAppForCase11) и прописать следующую команду: 
uvicorn main:app --reload
В дальнейшем необходимо перейти на локальный ip. 


### Необходимые Условия

- Python 3.10
- FastAPI
- uvicorn
- jinja2

### Установка Пакета

pip install .
pip install git+https://github.com/cvg/LightGlue.git@main

### Гененрация синтетических изображений

Для генерации изображений для обучения модели используется графический редактор Blender, в котором присутствует возможность задавать собственные скрипты для создания и рендера сцены.

Установка Blender:

```bash
wget https://download.blender.org/release/Blender3.6/blender-3.6.0-linux-x64.tar.xz
tar -xvf blender-3.6.0-linux-x64.tar.xz
rm blender-3.6.0-linux-x64.tar.xz
```

Скрипт для генерации изображений лежит по пути `scripts/render.sh`. В нем необходимо указать путь до объекта для рендера и директорию, куда сохранить сгенерированные изображения.

После запуска скрипта должна получится следующая структура:

```
- save_dir
    - pair_0
        - image_left.png
        - image_right.png
    - pair_1
        - image_left.png
        - image_right.png
    ...
```

где в папках `pair_*` лежат сгенерированные пары изображений с рандомными поворотами по оси Z.
