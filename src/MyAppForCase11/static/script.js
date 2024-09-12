document.addEventListener('DOMContentLoaded', function() {
    // Изначально скрываем секцию параметров камеры и секцию загрузки модели
    document.getElementById('camera-params-section').style.display = 'none';
    document.getElementById('model-upload-section').style.display = 'none';
});

// Логика кнопки "Upload Calibration"
document.getElementById('calibration-btn').addEventListener('click', async function() {
    const calibrationInput = document.getElementById('calibration_file');

    if (calibrationInput.files.length === 0) {
        alert('Пожалуйста, загрузите файл калибровки.');
        return;
    }

    const formData = new FormData();
    formData.append('calibration_file', calibrationInput.files[0]);

    try {
        const response = await fetch('/upload_calibration/', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.result);
        } else {
            alert(result.error);
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
});

// Логика кнопки "Upload Parameters"
document.getElementById('upload-params-btn').addEventListener('click', async function() {
    const focalLength = document.getElementById('focal_length').value;
    const pixelSize = document.getElementById('pixel_size').value;
    const sensorResolution = document.getElementById('sensor_resolution').value;
    const sensorSize = document.getElementById('sensor_size').value;
    const distance = document.getElementById('distance').value;
    const chessboardImage1 = document.getElementById('chessboard_image1').files[0];
    const chessboardImage2 = document.getElementById('chessboard_image2').files[0];
    const numTiles = document.getElementById('tiles').value;
    const squareSize = document.getElementById('square_size').value;

    // Проверка заполненности полей и загрузки файлов
    if (!focalLength || !pixelSize || !sensorResolution || !sensorSize || !distance || !chessboardImage1 || !chessboardImage2 || !numTiles || !squareSize) {
        alert('Пожалуйста, заполните все поля и загрузите оба изображения шахматной доски.');
        return;
    }

    const formData = new FormData();
    formData.append('focal_length', focalLength);
    formData.append('pixel_size', pixelSize);
    formData.append('sensor_resolution', sensorResolution);
    formData.append('sensor_size', sensorSize);
    formData.append('distance', distance);
    formData.append('chessboard_image1', chessboardImage1);
    formData.append('chessboard_image2', chessboardImage2);
    formData.append('num_tiles', numTiles);  // Исправлено на 'num_tiles'
    formData.append('square_size', squareSize);

    try {
        const response = await fetch('/upload_params/', {
            method: 'POST',
            body: formData
        });

        // Проверка статуса ответа
        if (response.ok) {
            const result = await response.json();
            document.getElementById('focal_length_display').innerText = result.focal_length;
            document.getElementById('pixel_size_display').innerText = result.pixel_size;
            document.getElementById('sensor_resolution_display').innerText = result.sensor_resolution;
            document.getElementById('sensor_size_display').innerText = result.sensor_size;
            document.getElementById('distance_display').innerText = result.distance;
            document.getElementById('tiles_display').innerText = result.num_tiles;  // Исправлено на 'num_tiles'
            document.getElementById('square_size_display').innerText = result.square_size;
            alert('Параметры успешно загружены.');
        } else {
            const result = await response.json();
            alert(`Ошибка: ${result.error}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при загрузке данных. Пожалуйста, попробуйте снова.');
    }
});

// Логика кнопки "Upload 3D Models and Process"
document.getElementById('upload-model-btn').addEventListener('click', async function() {
    const imagesCount = document.getElementById('images_count').value;
    const modelFile = document.getElementById('model_file');

    if (!imagesCount || modelFile.files.length === 0) {
        alert('Пожалуйста, укажите количество изображений и загрузите модель.');
        return;
    }

    const formData = new FormData();
    formData.append('images_count', imagesCount);
    formData.append('model_file', modelFile.files[0]);

    try {
        const response = await fetch('/upload_model/', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (response.ok) {
            document.getElementById('images_count_display').innerText = result.images_count;
            document.getElementById('action_result').innerText = result.result;
        } else {
            alert(result.error);
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
});

// Логика кнопки "Upload and Process"
document.getElementById('upload-and-process-btn').addEventListener('click', async function() {
    const image1Input = document.getElementById('image1');
    const image2Input = document.getElementById('image2');

    if (image1Input.files.length === 0 || image2Input.files.length === 0) {
        alert('Пожалуйста, загрузите оба изображения.');
        return;
    }

    const formData = new FormData();
    formData.append('image1', image1Input.files[0]);
    formData.append('image2', image2Input.files[0]);

    try {
        const response = await fetch('/upload_and_process/', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (response.ok) {
            document.getElementById('action_result').innerText = result.result;
        } else {
            alert(result.error);
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
});

// Логика переключателя "Calibration Mode"
document.getElementById('calibration-toggle').addEventListener('change', function() {
    const isChecked = this.checked;
    document.getElementById('calibration-section').style.display = isChecked ? 'none' : 'block';
    document.getElementById('camera-params-section').style.display = isChecked ? 'block' : 'none';
});

// Логика переключателя "3D Model Upload Mode"
document.getElementById('model-toggle').addEventListener('change', function() {
    const isChecked = this.checked;
    document.getElementById('image-upload-section').style.display = isChecked ? 'none' : 'block';
    document.getElementById('model-upload-section').style.display = isChecked ? 'block' : 'none';
});
