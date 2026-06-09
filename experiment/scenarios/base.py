from typing import Protocol

from experiment.clients import RobotClients
from experiment.detection import Detection


class ActivityScenario(Protocol):
    def start(self, clients: RobotClients) -> None:
        ...

    def handle_detections(self, detections: list[Detection]) -> None:
        ...