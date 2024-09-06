document.getElementById('switch').addEventListener('change', function() {
    const is3DMode = this.checked;
    document.getElementById('image-upload-section').style.display = is3DMode ? 'none' : 'block';
    document.getElementById('model-upload-title').style.display = is3DMode ? 'block' : 'none';
    document.getElementById('model-upload-section').style.display = is3DMode ? 'block' : 'none';
});

document.getElementById('process-btn').addEventListener('click', async function() {
    const params = ['focal_length', 'pixel_size', 'sensor_resolution', 'sensor_size', 'distance'];
    const formData = new FormData();
    let allFilled = true;

    // Проверка полей формы Camera Parameters and Distance
    params.forEach(param => {
        const value = document.getElementById(param).value;
        console.log(`Parameter: ${param}, Value: ${value}, Type: ${typeof value}`);

        if (!value) {
            allFilled = false;
            document.getElementById(param).classList.add('error');
        } else {
            document.getElementById(param).classList.remove('error');
        }
        formData.append(param, value);
    });

    // Проверка загрузки файлов (фото или модели)
    const imageInput1 = document.getElementById('image1');
    const imageInput2 = document.getElementById('image2');
    const modelInput = document.getElementById('model');
    const is3DMode = document.getElementById('switch').checked;

    let filesValid = false;

    if (is3DMode) {
        if (modelInput.files.length > 0) {
            console.log(`Model File: ${modelInput.files[0].name}, Type: ${typeof modelInput.files[0]}`);
            formData.append('model', modelInput.files[0]);
            filesValid = true;
        }
    } else {
        if (imageInput1.files.length > 0 && imageInput2.files.length > 0) {
            console.log(`First Image File: ${imageInput1.files[0].name}, Type: ${typeof imageInput1.files[0]}`);
            console.log(`Second Image File: ${imageInput2.files[0].name}, Type: ${typeof imageInput2.files[0]}`);
            formData.append('image1', imageInput1.files[0]);
            formData.append('image2', imageInput2.files[0]);
            filesValid = true;
        }
    }

    if (!allFilled || !filesValid) {
        alert("Please fill in all fields and upload required files.");
        return;
    }

    // Отправляем данные на сервер
    try {
        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            params.forEach(param => {
                document.getElementById(param + '_display').innerText = document.getElementById(param).value;
            });
            document.getElementById('action_result').innerText = data.result;
            console.log("Server Response:", data);
        } else {
            throw new Error(`Upload failed with status ${response.status}`);
        }
    } catch (error) {
        console.error('Error during upload:', error);
        document.getElementById('action_result').innerText = "An error occurred. Please try again.";
    }
});
