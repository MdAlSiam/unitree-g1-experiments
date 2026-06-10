from typing import Protocol

from experiment.detection import Detection


class Detector(Protocol):
    def detect(self, frame) -> list[Detection]:
        """Analyze a frame and return the detections found in it."""
        ...