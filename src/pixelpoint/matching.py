import argparse
from pathlib import Path
from typing import NamedTuple

import cv2
import numpy as np


class Circle(NamedTuple):
    idx: int  # circle ID
    y: int  # circle coord by height
    x: int  # circle coord by width


def match_circles(image_left: np.ndarray, image_right: np.ndarray) -> tuple[list[Circle], list[Circle]]:
    # Find homography between the two images
    homography_matrix = _find_homography_sift(image_left, image_right)

    # Detect circles in the left image
    circles_left = _detect_circles(image_left)

    # Map detected circles to the right image using the homography
    circles_right = _map_circles_homography(circles_left, homography_matrix)

    return list(zip(circles_left, circles_right))


# pylint: disable=too-many-locals
def _find_homography_sift(image_left: np.ndarray, image_right: np.ndarray) -> np.ndarray:
    # Step 1: Detect keypoints and descriptors using SIFT
    sift = cv2.SIFT_create()
    kp_left, des_left = sift.detectAndCompute(image_left, None)
    kp_right, des_right = sift.detectAndCompute(image_right, None)

    # Step 2: Match descriptors using FLANN-based matcher
    flann_index_kdtree = 1
    index_params = {"algorithm": flann_index_kdtree, "trees": 5}
    search_params = {"checks": 50}  # or pass empty dictionary

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des_left, des_right, k=2)

    # Step 3: Apply ratio test to keep good matches
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    if len(good_matches) <= 4:
        raise ValueError(f"Not enough matches are found - {len(good_matches)}/{4}")

    # Step 4: Find homography if enough good matches are found
    src_pts = np.float32([kp_left[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp_right[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # Compute the homography matrix using RANSAC
    homography_matrix, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    return homography_matrix


def _detect_circles(image: np.ndarray) -> list[Circle]:
    # Step 2: Detect circles in the left image using HoughCircles
    circles = cv2.HoughCircles(
        image, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100, param1=50, param2=30, minRadius=40, maxRadius=80
    )

    if circles is None:
        return []

    circles = np.round(circles[0, :]).astype("int")
    return [Circle(idx=i, x=c[0].item(), y=c[1].item()) for i, c in enumerate(circles)]


def _map_circles_homography(circles_left: list[Circle], homography_matrix: np.ndarray) -> list[Circle]:
    # Step 3: Use homography to find corresponding circles in the right image
    points_left = np.array([[circle.x, circle.y] for circle in circles_left], dtype=np.float32)[None, ...]

    # Transform the points using the homography matrix
    points_right = cv2.perspectiveTransform(points_left, homography_matrix)

    # Convert transformed points to Circle objects
    circles_right = [
        Circle(idx=circles_left[i].idx, x=int(pt[0]), y=int(pt[1])) for i, pt in enumerate(points_right[0])
    ]
    return circles_right


def main():
    np.random.seed(42)

    parser = argparse.ArgumentParser(description="Match circles on paired images.")
    parser.add_argument("--left-image-path", type=str, required=True, help="")
    parser.add_argument("--right-image-path", type=str, required=True, help="")
    parser.add_argument("--output-dir", type=str, required=True, help="Directory to save images with visualization.")
    args = parser.parse_args()

    image_left = cv2.imread(args.left_image_path)
    image_left = cv2.cvtColor(image_left, cv2.COLOR_BGR2GRAY)

    image_right = cv2.imread(args.right_image_path)
    image_right = cv2.cvtColor(image_right, cv2.COLOR_BGR2GRAY)

    matches = match_circles(image_left=image_left, image_right=image_right)

    draw_image_left = cv2.cvtColor(image_left, cv2.COLOR_GRAY2RGB)
    draw_image_right = cv2.cvtColor(image_right, cv2.COLOR_GRAY2RGB)

    for i, (matches_left, matches_right) in enumerate(matches):
        color_int = np.random.randint(128, 255, 1).item()
        color = [0 for _ in range(3)]
        color[i % 3] = color_int

        draw_image_left = cv2.circle(draw_image_left, (matches_left.x, matches_left.y), 10, color, 20)
        draw_image_right = cv2.circle(draw_image_right, (matches_right.x, matches_right.y), 10, color, 20)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    cv2.imwrite((output_dir / "image_left.png").as_posix(), draw_image_left)
    cv2.imwrite((output_dir / "image_right.png").as_posix(), draw_image_right)
