from dataclasses import dataclass


DEFAULT_GST_PIPELINE_TEMPLATE = (
    "udpsrc address=230.1.1.1 port=1720 multicast-iface={network_interface} ! "
    "application/x-rtp,media=video,encoding-name=H264 ! "
    "rtpjitterbuffer latency=0 ! "
    "rtph264depay ! "
    "h264parse ! "
    "avdec_h264 ! "
    "videoconvert ! "
    "appsink drop=true max-buffers=1 sync=false"
)


@dataclass(frozen=True)
class ExperimentConfig:
    network_interface: str = "enp130s0"
    model_path: str = "yolov8n.pt"
    detection_confidence: float = 0.65
    alert_interval_seconds: float = 3.0
    welcome_pause_seconds: float = 1.5
    confirmation_frames: int = 1
    fps_log_interval: int = 100
    output_path: str = "debug.jpg"

    def gst_pipeline(self) -> str:
        return DEFAULT_GST_PIPELINE_TEMPLATE.format(
            network_interface=self.network_interface
        )