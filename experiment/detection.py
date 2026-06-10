from dataclasses import dataclass

import cv2


@dataclass(frozen=True)
class Detection:
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float


def annotate_frame(frame, detections: list[Detection]):
    """Draw detection bounding boxes on the provided frame and return it."""
    for detection in detections:
        cv2.rectangle(
            frame,
            (detection.x1, detection.y1),
            (detection.x2, detection.y2),
            (0, 255, 0),
            2,
        )

    return frame