import time
from dataclasses import dataclass, field

from experiment.clients import RobotClients
from experiment.detection import Detection


@dataclass
class WelcomeWaveScenario:
    pause_seconds: float = 3.0
    alert_interval_seconds: float = 5.0
    confirmation_frames: int = 3
    clients: RobotClients | None = field(default=None, init=False)
    last_alert_time: float = field(default=0.0, init=False)
    consecutive_detection_frames: int = field(default=0, init=False)

    def start(self, clients: RobotClients) -> None:
        """Store the robot clients and play the welcome audio sequence."""
        self.clients = clients
        self.clients.audio_client.TtsMaker("Welcome to tuskeegi University.", 1)
        time.sleep(self.pause_seconds)
        self.clients.audio_client.TtsMaker("Greeeting, President Doctor Brown.", 1)
        time.sleep(self.pause_seconds)
        self.clients.audio_client.TtsMaker("Thank you for your support.", 1)
        time.sleep(self.pause_seconds)

    def handle_detections(self, detections: list[Detection]) -> None:
        """Confirm repeated detections, then trigger the robot response."""
        if not detections or self.clients is None:
            self.consecutive_detection_frames = 0
            return

        self.consecutive_detection_frames += 1
        if self.consecutive_detection_frames < self.confirmation_frames:
            return

        current_time = time.time()
        if (current_time - self.last_alert_time) <= self.alert_interval_seconds:
            return

        print(f"Face detected ({len(detections)}), confidences: {[d.confidence for d in detections]} - attempting ShakeHand")
        try:
            # result = self.clients.loco_client.WaveHand()
            result = self.clients.loco_client.ShakeHand()
            print(f"ShakeHand result: {result}")
        except Exception as e:
            print(f"ShakeHand call failed: {e}")
            import traceback

            traceback.print_exc()

        try:
            self.clients.audio_client.TtsMaker(f"{len(detections)} human detected" if len(detections) == 1 else f"{len(detections)} humans detected", 1)
        except Exception as e:
            print(f"TtsMaker failed: {e}")

        time.sleep(3)
        self.last_alert_time = current_time
        self.consecutive_detection_frames = 0
        self.consecutive_detection_frames = 0