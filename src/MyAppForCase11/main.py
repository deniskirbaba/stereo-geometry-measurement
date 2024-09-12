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
UPLOAD_CALIBRATION_PATH = "calibration"
UPLOAD_MODELS_PATH = "models"
UPLOAD_CALIBRATION_PHOTO_PATH = "calibration_photo"

os.makedirs(UPLOAD_IMAGES_PATH, exist_ok=True)
os.makedirs(UPLOAD_CALIBRATION_PATH, exist_ok=True)
os.makedirs(UPLOAD_MODELS_PATH, exist_ok=True)
os.makedirs(UPLOAD_CALIBRATION_PHOTO_PATH, exist_ok=True)

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/")
async def upload_data(image1: UploadFile = File(None), image2: UploadFile = File(None)):
    if image1 and image2:
        image1_path = os.path.join(UPLOAD_IMAGES_PATH, image1.filename)
        image2_path = os.path.join(UPLOAD_IMAGES_PATH, image2.filename)
        with open(image1_path, "wb") as buffer:
            buffer.write(await image1.read())
        with open(image2_path, "wb") as buffer:
            buffer.write(await image2.read())
    else:
        return JSONResponse(status_code=422, content={"error": "Images are missing"})

    return {"result": "0.05 мм"}

@app.post("/upload_calibration/")
async def upload_calibration(calibration_file: UploadFile = File(...)):
    if not calibration_file.filename.endswith(".json"):
        return JSONResponse(status_code=422, content={"error": "Only JSON files are allowed."})

    calibration_path = os.path.join(UPLOAD_CALIBRATION_PATH, calibration_file.filename)
    with open(calibration_path, "wb") as buffer:
        buffer.write(await calibration_file.read())

    return {"result": "Calibration file uploaded successfully."}

@app.post("/upload_params/")
async def upload_params(
    focal_length: str = Form(None),
    pixel_size: str = Form(None),
    sensor_resolution: str = Form(None),
    sensor_size: str = Form(None),
    distance: str = Form(None),
    num_tiles: str = Form(None),
    square_size: str = Form(None),
    chessboard_image1: UploadFile = File(None),
    chessboard_image2: UploadFile = File(None)
):
    if not all([focal_length, pixel_size, sensor_resolution, sensor_size, distance, num_tiles, square_size]):
        return JSONResponse(status_code=422, content={"error": "All fields must be provided."})

    if chessboard_image1 and chessboard_image2:
        chessboard_image1_path = os.path.join(UPLOAD_CALIBRATION_PHOTO_PATH, chessboard_image1.filename)
        chessboard_image2_path = os.path.join(UPLOAD_CALIBRATION_PHOTO_PATH, chessboard_image2.filename)
        with open(chessboard_image1_path, "wb") as buffer:
            buffer.write(await chessboard_image1.read())
        with open(chessboard_image2_path, "wb") as buffer:
            buffer.write(await chessboard_image2.read())
    else:
        return JSONResponse(status_code=422, content={"error": "Calibration chessboard images are missing."})

    return {
        "focal_length": focal_length,
        "pixel_size": pixel_size,
        "sensor_resolution": sensor_resolution,
        "sensor_size": sensor_size,
        "distance": distance,
        "num_tiles": num_tiles,
        "square_size": square_size,
        "result": "Calibration parameters uploaded successfully."
    }


@app.post("/upload_and_process/")
async def upload_and_process(image1: UploadFile = File(...), image2: UploadFile = File(...)):
    if image1 and image2:
        image1_path = os.path.join(UPLOAD_IMAGES_PATH, image1.filename)
        image2_path = os.path.join(UPLOAD_IMAGES_PATH, image2.filename)
        with open(image1_path, "wb") as buffer:
            buffer.write(await image1.read())
        with open(image2_path, "wb") as buffer:
            buffer.write(await image2.read())
        return {"result": "0.07 мм"}
    else:
        return JSONResponse(status_code=422, content={"error": "Images are missing"})

@app.post("/upload_model/")
async def upload_model(
        images_count: str = Form(None),
        model_file: UploadFile = File(None)
):
    if not images_count or not model_file:
        return JSONResponse(status_code=422, content={"error": "Images count and a model must be provided."})

    model_path = os.path.join(UPLOAD_MODELS_PATH, model_file.filename)
    with open(model_path, "wb") as buffer:
        buffer.write(await model_file.read())

    return {
        "images_count": images_count,
        "result": "0.05 мм"
    }

@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422,
                        content={"error": "Validation error. Please check all fields and file uploads."})
