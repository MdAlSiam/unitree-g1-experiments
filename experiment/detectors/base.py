from typing import Protocol

from experiment.detection import Detection


class Detector(Protocol):
    def detect(self, frame) -> list[Detection]:
        ...