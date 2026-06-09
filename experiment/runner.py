import argparse
import time
from datetime import datetime

import cv2

from experiment.clients import initialize_robot_clients
from experiment.config import ExperimentConfig
from experiment.detection import annotate_frame
from experiment.detectors.yolo_face import YoloFaceDetector
from experiment.scenarios.welcome_wave import WelcomeWaveScenario
from experiment.video import open_video_capture


def build_detector(name: str, config: ExperimentConfig):
    if name == "yolo_face":
        return YoloFaceDetector(
            model_path=config.model_path,
            confidence_threshold=config.detection_confidence,
        )

    raise ValueError(f"Unknown detector: {name}")


def build_scenario(name: str, config: ExperimentConfig):
    if name == "welcome_wave":
        return WelcomeWaveScenario(
            pause_seconds=config.welcome_pause_seconds,
            alert_interval_seconds=config.alert_interval_seconds,
            confirmation_frames=config.confirmation_frames,
        )

    raise ValueError(f"Unknown scenario: {name}")


def run_experiment(config: ExperimentConfig, detector_name: str, scenario_name: str) -> None:
    print(f"Using network interface: {config.network_interface}")
    clients = initialize_robot_clients(config.network_interface)

    scenario = build_scenario(scenario_name, config)
    scenario.start(clients)
    print(f"Clients initialized: {clients}")

    detector = build_detector(detector_name, config)

    capture = open_video_capture(config.gst_pipeline())

    count = 0
    start_time = time.time()

    while True:
        ret, frame = capture.read()

        if not ret:
            continue

        count += 1

        detections = detector.detect(frame)
        annotate_frame(frame, detections)

        try:
            scenario.handle_detections(detections)
        except Exception as exc:
            print(f"Error handling detections: {exc}")
            import traceback

            traceback.print_exc()

        if count % config.fps_log_interval == 0:
            fps = count / (time.time() - start_time)
            print(f"FPS: {fps:.2f}")
            print(f"Faces detected: {len(detections)}")

        blink_on = int(time.time() * 2) % 2 == 0
        if blink_on:
            cv2.putText(
                frame,
                "LIVE",
                (20, 40),
                cv2.FONT_HERSHEY_TRIPLEX,
                1.0,
                (0, 0, 255),
                2,
            )

        cv2.putText(
            frame,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            (110, 40),
            cv2.FONT_HERSHEY_TRIPLEX,
            1.0,
            (0, 255, 0),
            2,
        )

        cv2.putText(
            frame,
            f"# Human: {len(detections)}",
            (20, 80),
            cv2.FONT_HERSHEY_TRIPLEX,
            1.0,
            (0, 255, 0),
            2,
        )

        cv2.imwrite(config.output_path, frame)


def run_from_cli() -> None:
    parser = argparse.ArgumentParser(description="Run the Unitree G1 experiment loop")
    parser.add_argument(
        "network_interface",
        nargs="?",
        default="enp130s0",
        help="Network interface used for the robot connection",
    )
    parser.add_argument(
        "--detector",
        default="yolo_face",
        choices=("yolo_face",),
        help="Detection component to run",
    )
    parser.add_argument(
        "--scenario",
        default="welcome_wave",
        choices=("welcome_wave",),
        help="Activity sequence to run",
    )
    args = parser.parse_args()

    config = ExperimentConfig(network_interface=args.network_interface)
    run_experiment(config, detector_name=args.detector, scenario_name=args.scenario)