import torch
from ultralytics import YOLO

from experiment.detection import Detection


class YoloFaceDetector:
    def __init__(self, model_path: str, confidence_threshold: float) -> None:
        """Load the YOLO model and prepare it for face detection."""
        self.confidence_threshold = confidence_threshold
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # self.device = "cpu"
        print(f">>> >>> Using device: {self.device}")
        self.model = YOLO(model_path)
        self.model.to(self.device)

    def detect(self, frame) -> list[Detection]:
        """Run the YOLO model on a frame and keep high-confidence person detections."""
        results = self.model(frame, device=self.device, verbose=False)[0]
        detections: list[Detection] = []

        for box in results.boxes:
            cls = int(box.cls[0])
            confidence = float(box.conf[0])

            if cls == 0 and confidence > self.confidence_threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append(
                    Detection(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        confidence=confidence,
                    )
                )

        return detections