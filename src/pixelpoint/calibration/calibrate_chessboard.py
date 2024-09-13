import argparse
from pathlib import Path

import cv2 as cv
import numpy as np
from tqdm import trange

from .calibration_utils import find_and_check_image_resolution
from .calibration_utils import load_images
from .calibration_utils import save_calibration_params

"""
This module performs stereo camera calibration using chessboard patterns.

Requirements:

1. All images used for calibration must have the same resolution.

2. Images should be named properly in `images_folder`. The expected naming is:
     - for left camera images: prefix 'cam1_' (e.g., 'cam1_image1.jpg').
     - for right camera images: prefix 'cam2_' (e.g., 'cam2_image1.jpg').

"""


def parse_args():
    parser = argparse.ArgumentParser(description="Stereo Camera Calibration using chessboard")
    parser.add_argument(
        "--images_folder",
        type=Path,
        default=Path("notebooks/calibration/calibration_images_chessboard"),
        help="Path to the folder with marker images (default: notebooks/calibration/calibration_images_chessboard)",
    )
    parser.add_argument(
        "--square_size", type=float, default=0.01, help="Size of the squares on the chessboard (default 0.01)"
    )
    parser.add_argument(
        "--chessboard_size", type=str, default="7x7", help='Chessboard size, e.g., "7x7" (default: 7x7)'
    )
    parser.add_argument(
        "--output_file",
        type=Path,
        default=Path("calib_params.json"),
        help="Path to output JSON file (default: calib_params.json)",
    )
    return parser.parse_args()


def calibrate_camera_chessboard(imgs, img_resolution, square_size, chessboard_size, CM_guess=None, dist_guess=None):
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0 : chessboard_size[0], 0 : chessboard_size[1]].T.reshape(-1, 2)
    objp *= square_size

    objpoints = []  # 3D points in real-world space
    imgpoints = []  # 2D points in image plane

    for i in trange(len(imgs), desc="Calculating intrinsic parameters..."):
        img_key = list(imgs.keys())[i]
        img = imgs[img_key].copy()

        ret, corners = cv.findChessboardCorners(img, chessboard_size, None)

        if ret:
            objpoints.append(objp)
            corners = cv.cornerSubPix(img, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners)

    ret, CM, dist, _, _ = cv.calibrateCamera(objpoints, imgpoints, img_resolution, CM_guess, dist_guess)
    print(f"RMSE: {ret}")
    return CM, dist


def stereo_calibrate_chessboard(
    cam1_imgs, cam2_imgs, img_resolution, square_size, chessboard_size, CM, dist, R_guess=None, T_guess=None
):
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.0001)

    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0 : chessboard_size[0], 0 : chessboard_size[1]].T.reshape(-1, 2)
    objp *= square_size

    objpoints = []  # 3D points in real-world space
    imgpoints1 = []  # 2D points in image plane of cam1 (left)
    imgpoints2 = []  # 2D points in image plane of cam2 (right)

    for i in trange(len(cam1_imgs), desc="Calculating extrinsic parameters..."):
        img_key = list(cam1_imgs.keys())[i]
        img1 = cam1_imgs[img_key]
        img2 = cam2_imgs[img_key.replace("cam2", "cam1")]

        ret1, corners1 = cv.findChessboardCorners(img1, chessboard_size, None)
        ret2, corners2 = cv.findChessboardCorners(img2, chessboard_size, None)

        if ret1 and ret2:
            objpoints.append(objp)

            corners1 = cv.cornerSubPix(img1, corners1, (11, 11), (-1, -1), criteria)
            corners2 = cv.cornerSubPix(img2, corners2, (11, 11), (-1, -1), criteria)

            imgpoints1.append(corners1)
            imgpoints2.append(corners2)

    stereocalibration_flags = cv.CALIB_FIX_INTRINSIC

    RMSE, _, _, _, _, R, T, E, F = cv.stereoCalibrate(
        objpoints,
        imgpoints1,
        imgpoints2,
        CM,
        dist,
        CM,
        dist,
        img_resolution,
        R_guess,
        T_guess,
        flags=stereocalibration_flags,
        criteria=criteria,
    )

    print(f"Stereo Calibration RMSE: {RMSE}")
    return R, T, E, F


def main():
    args = parse_args()

    images_folder = Path(args.images_folder)
    square_size = args.square_size

    cam1_imgs, cam2_imgs = load_images(images_folder)
    if not cam1_imgs or not cam2_imgs:
        raise FileNotFoundError("No images found for one or both cameras.")

    img_resolution = find_and_check_image_resolution({**cam1_imgs, **cam2_imgs})
    chessboard_size = tuple(map(int, args.chessboard_size.split("x")))

    CM, dist = calibrate_camera_chessboard({**cam1_imgs, **cam2_imgs}, img_resolution, square_size, chessboard_size)
    R, T, E, F = stereo_calibrate_chessboard(
        cam1_imgs, cam2_imgs, img_resolution, square_size, chessboard_size, CM, dist
    )

    save_calibration_params(CM, dist, R, T, E, F, args.output_file)
    print(f"Calibration parameters saved to {args.output_file}")


if __name__ == "__main__":
    main()
