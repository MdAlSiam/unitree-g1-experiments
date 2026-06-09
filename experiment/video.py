import cv2


def open_video_capture(gst_pipeline: str):
    capture = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
    if not capture.isOpened():
        raise RuntimeError("Failed to open stream")

    return capture