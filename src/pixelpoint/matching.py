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
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(
        image, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100, param1=50, param2=30, minRadius=40, maxRadius=80
    )

    if circles is None:
        return []

    circles = np.round(circles[0, :]).astype("int")
    return [Circle(idx=i, x=c[0].item(), y=c[1].item()) for i, c in enumerate(circles)]


def _map_circles_homography(circles_left: list[Circle], homography_matrix: np.ndarray) -> list[Circle]:
    # Step 3: Use homography to find corresponding circles in the right image
    points_left = np.array([[circle.x, circle.y] for circle in circles_left], dtype=np.float32)
    points_left = np.array([points_left])

    # Transform the points using the homography matrix
    points_right = cv2.perspectiveTransform(points_left, homography_matrix)

    # Convert transformed points to Circle objects
    circles_right = [
        Circle(idx=circles_left[i].idx, x=int(pt[0]), y=int(pt[1])) for i, pt in enumerate(points_right[0])
    ]
    return circles_right
