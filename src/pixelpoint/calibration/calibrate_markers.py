import argparse
import json
from pathlib import Path

import cv2 as cv
import numpy as np

from .calibration_utils import find_and_check_image_resolution
from .calibration_utils import load_images
from .calibration_utils import save_calibration_params

"""
This module performs stereo camera calibration using images and marker coordinates.

Requirements:

1. All images used for calibration must have the same resolution.

2. Images should be named properly in `images_folder`. The expected naming is:
     - for left camera images: prefix 'cam1_' (e.g., 'cam1_image1.jpg').
     - for right camera images: prefix 'cam2_' (e.g., 'cam2_image1.jpg').

3. The marker coordinates should be provided in a JSON file specified by `markers_file`.
The JSON file should have the following structure:
     {
       "image_name": ["x1,y1", "x2,y2", ...],
       ...
     }

4. The distance between marker points, specified by `marker_distance`, should be consistent across all images.
The calibration assumes that all images use the same marker distance.
Notice, that this is not done for the images in default folder.

"""


def parse_args():
    parser = argparse.ArgumentParser(description="Stereo Camera Calibration using markers coordinates")
    parser.add_argument(
        "--images_folder",
        type=Path,
        default=Path("notebooks/calibration/calibration_images_markers"),
        help="Path to the folder with marker images (default: notebooks/calibration/calibration_images_markers)",
    )
    parser.add_argument(
        "--markers_file",
        type=Path,
        default=Path("notebooks/calibration/calibration_params/markers_coords.json"),
        help="Path to JSON file with coordinates of marker points on the image \
            (default: notebooks/calibration/calibration_params/markers_coords.json)",
    )
    parser.add_argument(
        "--marker_distance", type=float, default=0.011, help="Distance between marker points in meters (default: 0.011)"
    )
    parser.add_argument("--grid_size", type=str, default="7x7", help='Marker grid size, e.g., "7x7" (default: 7x7)')
    parser.add_argument(
        "--output_file",
        type=Path,
        default=Path("calib_params.json"),
        help="Path to output JSON file (default: calib_params.json)",
    )
    return parser.parse_args()


def load_marker_coords(markers_file):
    with markers_file.open("r") as file:
        markers_coords = json.load(file)
    for img_name, coords in markers_coords.items():
        markers_coords[img_name] = [tuple(map(int, point.split(","))) for point in coords]
    return markers_coords


def calibrate_camera_markers(imgs, img_resolution, markers_coords, marker_dist, grid_shape):
    rows, columns = grid_shape
    real_markers = []
    img_markers = []
    for img_name in imgs:
        markers = np.array(markers_coords[img_name], dtype=np.float32)
        img_markers.append(markers)
        real_markers_grid_coords = np.zeros((rows * columns, 3), np.float32)
        real_markers_grid_coords[:, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
        real_markers_grid_coords *= marker_dist
        real_markers.append(real_markers_grid_coords)
    ret, CM, dist, _, _ = cv.calibrateCamera(real_markers, img_markers, img_resolution, None, None)
    print(f"Camera Calibration RMSE: {ret}")
    return CM, dist


def stereo_calibrate_markers(cam1_imgs, cam2_imgs, img_resolution, markers_coords, marker_dist, grid_shape, CM, dist):
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 1000, 1e-6)
    rows, columns = grid_shape
    real_markers = []
    cam1_img_markers = []
    cam2_img_markers = []
    for cam1_img_name, cam2_img_name in zip(cam1_imgs, cam2_imgs):
        cam1_markers = marker_dist
        real_markers_grid_coords = np.zeros((rows * columns, 3), np.float32)
        real_markers_grid_coords[:, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
        real_markers_grid_coords *= cam1_markers
        real_markers.append(real_markers_grid_coords)
        cam1_img_markers.append(np.array(markers_coords[cam1_img_name], dtype=np.float32))
        cam2_img_markers.append(np.array(markers_coords[cam2_img_name], dtype=np.float32))
    stereocalibration_flags = cv.CALIB_FIX_INTRINSIC
    ret, _, _, _, _, R, T, E, F = cv.stereoCalibrate(
        real_markers,
        cam1_img_markers,
        cam2_img_markers,
        CM,
        dist,
        CM,
        dist,
        img_resolution,
        None,
        None,
        criteria=criteria,
        flags=stereocalibration_flags,
    )
    print(f"Stereo Calibration RMSE: {ret}")
    return R, T, E, F


def main():
    args = parse_args()

    cam1_imgs, cam2_imgs = load_images(args.images_folder)
    if not cam1_imgs or not cam2_imgs:
        raise FileNotFoundError("No images found for one or both cameras.")

    markers_coords = load_marker_coords(args.markers_file)

    img_resolution = find_and_check_image_resolution({**cam1_imgs, **cam2_imgs})
    grid_shape = tuple(map(int, args.grid_size.split("x")))
    marker_dist = args.marker_distance

    CM, dist = calibrate_camera_markers(
        {**cam1_imgs, **cam2_imgs}, img_resolution, markers_coords, marker_dist, grid_shape
    )
    R, T, E, F = stereo_calibrate_markers(
        cam1_imgs, cam2_imgs, img_resolution, markers_coords, marker_dist, grid_shape, CM, dist
    )

    save_calibration_params(CM, dist, R, T, E, F, args.output_file)
    print(f"Calibration parameters saved to {args.output_file}")


if __name__ == "__main__":
    main()
