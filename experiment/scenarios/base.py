from typing import Protocol

from experiment.clients import RobotClients
from experiment.detection import Detection


class ActivityScenario(Protocol):
    def start(self, clients: RobotClients) -> None:
        """Perform any one-time setup before the detection loop starts."""
        ...

    def handle_detections(self, detections: list[Detection]) -> None:
        """React to the current frame's detections and update scenario state."""
        ...