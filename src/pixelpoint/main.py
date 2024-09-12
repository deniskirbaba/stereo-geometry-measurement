import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import uvicorn
from fastapi import FastAPI
from fastapi import File
from fastapi import Form
from fastapi import UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from pixelpoint.matching import draw_images_with_circles
from pixelpoint.matching import match_circles
from pixelpoint.render import render_paired_images

app = FastAPI()

ROOT_DIR = Path(__file__).parent
STATIC_DIR = ROOT_DIR / "static"
TEMPLATES_DIR = ROOT_DIR / "templates"

ARTEFACTS_DIR = Path().cwd() / "artefacts"
UPLOAD_IMAGES_PATH = ARTEFACTS_DIR / "camera_images"
MATCHED_CIRCLES_ON_IMAGES_PATH = ARTEFACTS_DIR / "circle_images"
RENDERED_IMAGES_BY_OBJECT_PATH = ARTEFACTS_DIR / "rendered_images"
UPLOAD_CALIBRATION_PATH = ARTEFACTS_DIR / "calibration"
UPLOAD_MODELS_PATH = ARTEFACTS_DIR / "models"
UPLOAD_CALIBRATION_PHOTO_PATH = ARTEFACTS_DIR / "calibration_photo"

UPLOAD_IMAGES_PATH.mkdir(exist_ok=True, parents=True)
UPLOAD_CALIBRATION_PATH.mkdir(exist_ok=True, parents=True)
UPLOAD_MODELS_PATH.mkdir(exist_ok=True, parents=True)
UPLOAD_CALIBRATION_PHOTO_PATH.mkdir(exist_ok=True, parents=True)
MATCHED_CIRCLES_ON_IMAGES_PATH.mkdir(exist_ok=True, parents=True)
RENDERED_IMAGES_BY_OBJECT_PATH.mkdir(exist_ok=True, parents=True)

templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/")
async def upload_data(image1: UploadFile = File(None), image2: UploadFile = File(None)):
    if image1 and image2:
        image1_path = UPLOAD_IMAGES_PATH / image1.filename
        image2_path = UPLOAD_IMAGES_PATH / image2.filename
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

    calibration_path = UPLOAD_CALIBRATION_PATH / calibration_file.filename
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
    chessboard_image2: UploadFile = File(None),
):
    if not all([focal_length, pixel_size, sensor_resolution, sensor_size, distance, num_tiles, square_size]):
        return JSONResponse(status_code=422, content={"error": "All fields must be provided."})

    if chessboard_image1 and chessboard_image2:
        chessboard_image1_path = UPLOAD_CALIBRATION_PHOTO_PATH / chessboard_image1.filename
        chessboard_image2_path = UPLOAD_CALIBRATION_PHOTO_PATH / chessboard_image2.filename
        with open(chessboard_image1_path, "wb") as buffer:
            buffer.write(await chessboard_image1.read())
        with open(chessboard_image2_path, "wb") as buffer:
            buffer.write(await chessboard_image2.read())
    else:
        return JSONResponse(status_code=422, content={"error": "Calibration chessboard images are missing."})

    params = {
        "focal_length": focal_length,
        "pixel_size": pixel_size,
        "sensor_resolution": sensor_resolution,
        "sensor_size": sensor_size,
        "distance": distance,
        "num_tiles": num_tiles,
        "square_size": square_size,
        "result": "Calibration parameters uploaded successfully.",
    }
    with open(UPLOAD_CALIBRATION_PATH / "calib.json", "w", encoding="utf-8") as f:
        json.dump(params, f)


@app.post("/upload_and_process/")
async def upload_and_process(image1: UploadFile = File(...), image2: UploadFile = File(...)):
    if image1 and image2:
        image1_path = UPLOAD_IMAGES_PATH / image1.filename
        image2_path = UPLOAD_IMAGES_PATH / image2.filename
        with open(image1_path, "wb") as buffer:
            buffer.write(await image1.read())
        with open(image2_path, "wb") as buffer:
            buffer.write(await image2.read())

        image_left = plt.imread(image1_path)
        image_right = plt.imread(image2_path)

        circles = match_circles(
            image_left=image_left,
            image_right=image_right,
        )
        draw_image_left, draw_image_right = draw_images_with_circles(
            image_left=image_left,
            image_right=image_right,
            circles=circles,
        )
        plt.imsave(MATCHED_CIRCLES_ON_IMAGES_PATH / image1_path.name, draw_image_left)
        plt.imsave(MATCHED_CIRCLES_ON_IMAGES_PATH / image2_path.name, draw_image_right)

        return {"result": f"Path to saved images with circles: {MATCHED_CIRCLES_ON_IMAGES_PATH.as_posix()}"}
    return JSONResponse(status_code=422, content={"error": "Images are missing"})


@app.post("/upload_model/")
async def upload_model(images_count: str = Form(None), model_file: UploadFile = File(None)):
    if not images_count or not model_file:
        return JSONResponse(status_code=422, content={"error": "Images count and a model must be provided."})

    model_path = UPLOAD_MODELS_PATH / model_file.filename
    with open(model_path, "wb") as buffer:
        buffer.write(await model_file.read())

    output_dir = RENDERED_IMAGES_BY_OBJECT_PATH / model_path.stem
    for i in range(int(images_count)):
        render_paired_images(
            object_path=model_path,
            output_dir=output_dir / f"pair_{i}",
        )

    return {"images_count": images_count, "result": f"Path to rendered images: {output_dir.as_posix()}"}


@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    del request
    del exc

    return JSONResponse(
        status_code=422, content={"error": "Validation error. Please check all fields and file uploads."}
    )


def run_server(host: str, port: int):
    uvicorn.run(app, host=host, port=port)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()
    run_server(host=args.host, port=args.port)
