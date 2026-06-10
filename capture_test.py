import cv2
import time
import sys
from datetime import datetime
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
from ultralytics import YOLO
import torch

gst_pipeline = (
    "udpsrc address=230.1.1.1 port=1720 multicast-iface=enp130s0 ! "
    "application/x-rtp,media=video,encoding-name=H264 ! "
    "rtpjitterbuffer latency=0 ! "
    "rtph264depay ! "
    "h264parse ! "
    "avdec_h264 ! "
    "videoconvert ! "
    "appsink drop=true max-buffers=1 sync=false"
)

# Initialize audio client
network_interface = sys.argv[1] if len(sys.argv) > 1 else "enp130s0"
print(f"Using network interface: {network_interface}")
ChannelFactoryInitialize(0, network_interface)

audio_client = AudioClient()
audio_client.SetTimeout(10.0)
audio_client.Init()

# Play welcome message
# audio_client.TtsMaker("Welcome to tuskeegi University", 1)
# time.sleep(3)
# audio_client.TtsMaker("Greeeting, President Doctor Brown.", 1)
# time.sleep(3)
# audio_client.TtsMaker("Thank you for your support", 1)
# time.sleep(3)

# Initialize arm client
loco_client = LocoClient()
loco_client.SetTimeout(10.0)
loco_client.Init()

print(f"LocoClient initialized")

# Load face detection model
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
model = YOLO("yolov8n.pt")
model.to(device)

cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    raise RuntimeError("Failed to open stream")

count = 0
start = time.time()
face_detected = False
last_face_alert = 0

while True:
    ret, frame = cap.read()

    if not ret:
        continue

    count += 1

    # Run face detection
    results = model(frame, device=device, verbose=False)[0]

    faces = []
    for box in results.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])

        if cls == 0 and conf > 0.5:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            faces.append((x1, y1, x2, y2))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Alert on face detection (throttle to every 5 seconds)
    current_time = time.time()
    if len(faces) > 0 and (current_time - last_face_alert) > 5:
        print("Face detected! Waving hand...")
        try:
            result = loco_client.WaveHand()
            print(f"WaveHand result: {result}")
            audio_client.TtsMaker(f"{len(faces)} humans detected", 1)
            time.sleep(3)
        except Exception as e:
            print(f"Error calling WaveHand: {e}")
            import traceback
            traceback.print_exc()
        last_face_alert = current_time

    if count % 100 == 0:
        fps = count / (time.time() - start)
        print(f"FPS: {fps:.2f}")
        print(f"Faces detected: {len(faces)}")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    cv2.putText(
        frame,
        f"Live {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        2,
    )

    cv2.putText(
        frame,
        f"# Human: {len(faces)}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        2,
    )

    cv2.imwrite("debug.jpg", frame)



# RUN BY: PYTHONPATH=/usr/lib/python3/dist-packages python3 capture_test.py (in .roboenv)