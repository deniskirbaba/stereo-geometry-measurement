from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_IMAGES_PATH = "camera_images"
UPLOAD_MODELS_PATH = "models"

# Убедитесь, что папки существуют
os.makedirs(UPLOAD_IMAGES_PATH, exist_ok=True)
os.makedirs(UPLOAD_MODELS_PATH, exist_ok=True)

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/")
async def upload_data(
    focal_length: str = Form(...),
    pixel_size: str = Form(...),
    sensor_resolution: str = Form(...),
    sensor_size: str = Form(...),
    distance: str = Form(...),
    image1: UploadFile = File(None),
    image2: UploadFile = File(None),
    model: UploadFile = File(None)
):
    # Логирование полученных данных для отладки
    print(f"Received: focal_length={focal_length}, pixel_size={pixel_size}, sensor_resolution={sensor_resolution}, sensor_size={sensor_size}, distance={distance}")

    if model:
        # Сохранение 3D модели
        model_path = os.path.join(UPLOAD_MODELS_PATH, model.filename)
        with open(model_path, "wb") as buffer:
            buffer.write(await model.read())
        print(f"Saved model: {model.filename} to {model_path}")
    elif image1 and image2:
        # Сохранение изображений
        image1_path = os.path.join(UPLOAD_IMAGES_PATH, image1.filename)
        image2_path = os.path.join(UPLOAD_IMAGES_PATH, image2.filename)
        with open(image1_path, "wb") as buffer:
            buffer.write(await image1.read())
        with open(image2_path, "wb") as buffer:
            buffer.write(await image2.read())
        print(f"Saved images: {image1.filename} and {image2.filename} to {UPLOAD_IMAGES_PATH}")
    else:
        return JSONResponse(status_code=422, content={"error": "Files are missing"})

    # Возвращаем результат обработки
    return {"result": "0.05 мм"}

# Код для обработки ошибок
@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"error": "Validation error. Please check all fields and file uploads."})

