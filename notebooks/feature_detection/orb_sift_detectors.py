import argparse
from pathlib import Path

import cv2
import matplotlib.pyplot as plt


def extract_keypoints_and_descriptors(img_1_path, img_2_path, detector_type="ORB"):
    img1 = cv2.imread(str(img_1_path), cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(str(img_2_path), cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        raise FileNotFoundError("One or both image paths are invalid or images cannot be read.")

    if detector_type == "ORB":
        detector = cv2.ORB_create(nfeatures=1000, nlevels=16)
    elif detector_type == "SIFT":
        detector = cv2.SIFT_create()
    else:
        raise ValueError(f"Unsupported detector type: {detector_type}. Use 'ORB' or 'SIFT'.")

    keypoints_1, descriptors_1 = detector.detectAndCompute(img1, None)
    keypoints_2, descriptors_2 = detector.detectAndCompute(img2, None)

    return (keypoints_1, descriptors_1), (keypoints_2, descriptors_2)


def draw_keypoints(img_1_path, kp1, img_2_path, kp2):
    img1 = cv2.imread(str(img_1_path))
    img2 = cv2.imread(str(img_2_path))

    img1_with_keypoints = cv2.drawKeypoints(
        img1, kp1, None, color=(0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    )
    img2_with_keypoints = cv2.drawKeypoints(
        img2, kp2, None, color=(0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    )

    img1_with_keypoints_rgb = cv2.cvtColor(img1_with_keypoints, cv2.COLOR_BGR2RGB)
    img2_with_keypoints_rgb = cv2.cvtColor(img2_with_keypoints, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.imshow(img1_with_keypoints_rgb)
    plt.axis("off")
    plt.title("Image 1 with Keypoints")

    plt.subplot(1, 2, 2)
    plt.imshow(img2_with_keypoints_rgb)
    plt.axis("off")
    plt.title("Image 2 with Keypoints")

    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Extract keypoints and descriptors from stereo images using ORB or SIFT."
    )
    parser.add_argument(
        "--detector",
        type=str,
        default="ORB",
        choices=["ORB", "SIFT"],
        help="Feature detector to use (ORB or SIFT). Default is ORB.",
    )
    parser.add_argument("--img1", type=Path, default=None, help="Path to the first image. Default is data/cam1_1.jpg.")
    parser.add_argument("--img2", type=Path, default=None, help="Path to the second image. Default is data/cam2_1.jpg.")

    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    default_img1_path = script_dir / "data" / "cam1_1.jpg"
    default_img2_path = script_dir / "data" / "cam2_1.jpg"

    img_1_path = args.img1 if args.img1 else default_img1_path
    img_2_path = args.img2 if args.img2 else default_img2_path

    try:
        (kp1, _), (kp2, _) = extract_keypoints_and_descriptors(img_1_path, img_2_path, detector_type=args.detector)

        print(f"Detector: {args.detector}")
        print(f"Keypoints in image 1: {len(kp1)}")
        print(f"Keypoints in image 2: {len(kp2)}")

        draw_keypoints(img_1_path, kp1, img_2_path, kp2)

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
