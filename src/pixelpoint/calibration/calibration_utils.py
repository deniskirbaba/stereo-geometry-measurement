import json

import cv2 as cv


def load_images(images_folder):
    cam1_imgs_paths = list(images_folder.glob("cam2_*.*"))
    cam2_imgs_paths = list(images_folder.glob("cam1_*.*"))
    cam1_imgs = {}
    cam2_imgs = {}

    for img_path in sorted(cam1_imgs_paths):
        img = cv.imread(str(img_path), 0)
        img_name = img_path.stem
        cam1_imgs[img_name] = img

    for img_path in sorted(cam2_imgs_paths):
        img = cv.imread(str(img_path), 0)
        img_name = img_path.stem
        cam2_imgs[img_name] = img

    return cam1_imgs, cam2_imgs


def find_and_check_image_resolution(images):
    if not images:
        raise ValueError("No images provided to determine resolution")

    resolution = None

    for img_name, img in images.items():
        if img is None:
            raise ValueError(f"Image data is missing or invalid for: {img_name}")

        current_resolution = (img.shape[1], img.shape[0])  # (width, height)

        if resolution is None:
            resolution = current_resolution
        elif resolution != current_resolution:
            raise ValueError(
                f"Image resolution mismatch: Expected {resolution}, but found {current_resolution} for image {img_name}"
            )

    if resolution is None:
        raise ValueError("No valid images found to determine resolution")

    return resolution


def save_calibration_params(CM, dist, R, T, E, F, output_path):
    calibration_data_json = {
        "CM": CM.tolist(),
        "dist": dist.tolist(),
        "R": R.tolist(),
        "T": T.tolist(),
        "E": E.tolist(),
        "F": F.tolist(),
    }
    with open(output_path, "w") as f:
        json.dump(calibration_data_json, f, indent=4)
