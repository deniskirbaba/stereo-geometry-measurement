import argparse
from pathlib import Path

import numpy as np

from .calibration_utils import save_calibration_params

"""
This module performs stereo camera calibration using raw parameters of camera/lens and optical setup configuration.
"""


def parse_args():
    parser = argparse.ArgumentParser(description="Stereo Camera Calibration using raw parameters")

    parser.add_argument("--focal-length", type=float, default=0.08, help="Focal length in meters (default 0.08)")
    parser.add_argument(
        "--resolution",
        type=str,
        default="5120x4096",
        help='Image resolution as "widthxheight", e.g., "1920x1080" (default: 5120x4096)',
    )
    parser.add_argument(
        "--pixel-size",
        type=lambda s: tuple(map(float, s.split(","))),
        default=(4.5e-6, 4.5e-6),
        help='Pixel size as "pixel_x,pixel_y" in meters (default: 4.5e-6, 4.5e-6)',
    )
    parser.add_argument(
        "--baseline", type=float, default=0.412, help="Baseline distance between cameras in meters (default: 0.412)"
    )
    parser.add_argument(
        "--cam2obj", type=float, default=0.650, help="Distance from cameras to the object in meters (default: 0.650)"
    )
    parser.add_argument(
        "--output_file",
        type=Path,
        default=Path("calib_params.json"),
        help="Path to output JSON file (default: calib_params.json)",
    )

    return parser.parse_args()


def calculate_CM(focal_length_m, img_resolution, pixel_sz_x, pixel_sz_y):
    width, height = img_resolution

    f_x = focal_length_m / pixel_sz_x
    f_y = focal_length_m / pixel_sz_y

    c_x = width / 2.0
    c_y = height / 2.0

    CM = np.array([[f_x, 0, c_x], [0, f_y, c_y], [0, 0, 1]])

    return CM


def create_rotation_matrix(rx, ry, rz):
    R_x = np.array([[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]])
    R_y = np.array([[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]])
    R_z = np.array([[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]])

    R = np.matmul(np.matmul(R_z, R_y), R_x)
    return R


def calculate_RT(baseline, cam2obj):
    # Set global coordinate system in between cameras

    # Calculating R
    alpha = np.pi / 2 - np.arccos(baseline / 2 / cam2obj)  # angle bw baseline and optical axis of camera (in rad)
    R1 = create_rotation_matrix(0, -alpha, 0)
    R2 = create_rotation_matrix(0, alpha, 0)

    R = np.dot(R2, R1.T)

    # Calculating T
    C1 = np.array([baseline / 2, 0.0, 0.0])  # Center of cam1 coord system
    C2 = np.array([-baseline / 2, 0.0, 0.0])  # Center of cam2 coord system

    # Translation vector
    t12_world = C2 - C1

    T = np.dot(R1.T, t12_world)

    return R, T


def calculate_E(R, T):
    # Compute skew-symmetric matrix [T]_x for the translation vector
    T_x = np.array([[0, -T[2], T[1]], [T[2], 0, -T[0]], [-T[1], T[0], 0]])

    E = np.dot(T_x, R)
    return E


def calculate_F(E, CM):
    F = np.dot(np.linalg.inv(CM).T, np.dot(E, np.linalg.inv(CM)))
    return F


def main():
    args = parse_args()

    resolution = tuple(map(int, args.resolution.split("x")))

    CM = calculate_CM(args.focal_length, resolution, args.pixel_size[0], args.pixel_size[1])
    dist = np.zeros(shape=(1, 5), dtype=np.float32)
    R, T = calculate_RT(args.baseline, args.cam2obj)
    E = calculate_E(R, T)
    F = calculate_F(E, CM)

    save_calibration_params(CM, dist, R, T, E, F, args.output_file)
    print(f"Calibration parameters saved to {args.output_file}")


if __name__ == "__main__":
    main()
