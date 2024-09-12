import argparse
from pathlib import Path

import cv2 as cv
import numpy as np
import torch
from matplotlib import pyplot as plt
from PIL import Image
from transformers import AutoImageProcessor
from transformers import SuperPointForKeypointDetection


def load_images(image_paths):
    return [Image.open(img_path).convert("RGB") for img_path in image_paths]


def process_images(images, processor):
    return processor(images, return_tensors="pt")


def superpoint_detect_keypoints(images, model, processor):
    inputs = process_images(images, processor)
    outputs = model(**inputs)

    results = []
    for i in range(len(images)):
        image_result = {}
        image_mask = outputs.mask[i]
        image_indices = torch.nonzero(image_mask).squeeze()
        image_result["keypoints"] = outputs.keypoints[i][image_indices]
        image_result["scores"] = outputs.scores[i][image_indices]
        image_result["descriptors"] = outputs.descriptors[i][image_indices]
        image_result["input_image"] = inputs["pixel_values"][i]
        results.append(image_result)

    return results


def superpoint_draw_keypoints(image_np, keypoints, color=(0, 0, 255), radius=2):
    for keypoint in keypoints:
        keypoint_x, keypoint_y = int(keypoint[0].item()), int(keypoint[1].item())
        image_np = cv.circle(image_np, (keypoint_x, keypoint_y), radius, color, thickness=-1)
    return image_np


def superpoint_visualize_keypoints(image_results):
    processed_images = []
    for result in image_results:
        image_np = np.transpose(result["input_image"], (1, 2, 0)).numpy()

        if image_np.max() <= 1.0:
            image_np = (image_np * 255).astype(np.uint8)
        else:
            image_np = image_np.astype(np.uint8)

        image_np = np.ascontiguousarray(image_np)

        image_np = superpoint_draw_keypoints(image_np, result["keypoints"])

        processed_images.append(cv.cvtColor(image_np, cv.COLOR_BGR2RGB))

    plt.figure(figsize=(10, 5))
    for i, img in enumerate(processed_images):
        plt.subplot(1, 2, i + 1)
        plt.imshow(img)
        plt.axis("off")
    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Feature Detection using SuperPoint")
    parser.add_argument(
        "--image1",
        type=Path,
        default=Path("notebooks/feature_detection/data/cam2_1.jpg"),
        help="Path to the first image. Default is 'notebooks/feature_detection/data/cam2_1.jpg'.",
    )
    parser.add_argument(
        "--image2",
        type=Path,
        default=Path("notebooks/feature_detection/data/cam1_1.jpg"),
        help="Path to the second image. Default is 'notebooks/feature_detection/data/cam1_1.jpg'.",
    )

    args = parser.parse_args()

    img_1_path = args.image1
    img_2_path = args.image2
    image_paths = [img_1_path, img_2_path]

    images = load_images(image_paths)

    processor = AutoImageProcessor.from_pretrained("magic-leap-community/superpoint")
    model = SuperPointForKeypointDetection.from_pretrained("magic-leap-community/superpoint")

    image_results = superpoint_detect_keypoints(images, model, processor)
    superpoint_visualize_keypoints(image_results)


if __name__ == "__main__":
    main()
