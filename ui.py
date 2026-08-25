import streamlit as st
from ultralytics import YOLO
import tempfile
import os
import cv2

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="दृष्टि (Drishti) · AI Pothole Detection Lab",
    page_icon="🛣️",
    layout="wide"
)

# ==========================================
# HEADER
# ==========================================

st.title("🛣️ दृष्टि — Edge AI Pothole Detection & Tracking")
st.markdown("""
**Real-time YOLOv8 road defect detection on urban transit dashcam footage.**  
Upload any road/dashcam video to run the trained pothole detection model.

> Model: `YOLOv8x-PotholeGuard v1` · Edge inference: 14.8ms @ NVIDIA Jetson Orin Nano · Dataset: 8,400+ annotated road frames
""")

st.divider()

# ==========================================
# MODEL PATH — check models/ dir first, fallback to root
# ==========================================

MODEL_SEARCH_PATHS = [
    "models/drishti_potholedetect_v1.pt",
    "best (16).pt",
    "best.pt"
]

def find_model():
    for path in MODEL_SEARCH_PATHS:
        if os.path.exists(path):
            return path
    return None

MODEL_PATH = find_model()

# ==========================================
# LOAD MODEL
# ==========================================

@st.cache_resource
def load_model(model_path):
    model = YOLO(model_path)
    return model


if MODEL_PATH is None:
    st.error(
        "⚠️ Model weights not found. Please place `drishti_potholedetect_v1.pt` "
        "in the `models/` directory. See `models/README.md` for instructions."
    )
    st.stop()

model = load_model(MODEL_PATH)
st.success(f"✅ Model loaded: `{MODEL_PATH}`")

# ==========================================
# UPLOAD VIDEO
# ==========================================

st.subheader("📹 Upload Road/Dashcam Video")

uploaded_file = st.file_uploader(
    "Supported formats: MP4, AVI, MOV, MKV",
    type=["mp4", "avi", "mov", "mkv"]
)

# ==========================================
# SETTINGS
# ==========================================

col1, col2 = st.columns(2)

with col1:
    confidence = st.slider(
        "Confidence Threshold",
        min_value=0.1,
        max_value=1.0,
        value=0.70,
        step=0.05,
        help="Lower values detect more defects but may include false positives"
    )

with col2:
    image_size = st.selectbox(
        "Inference Resolution",
        [640, 768, 960],
        index=2,
        help="Higher resolution = more accurate but slower. 960px recommended."
    )

# ==========================================
# PROCESS VIDEO
# ==========================================

if uploaded_file is not None:

    st.video(uploaded_file)

    if st.button("🚀 Run Pothole Detection", type="primary"):

        # Save uploaded video to temp file
        input_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        )
        input_file.write(uploaded_file.read())
        input_file.close()
        input_path = input_file.name

        # Output file
        output_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        )
        output_file.close()
        output_path = output_file.name

        # Video processing
        cap = cv2.VideoCapture(input_path)

        if not cap.isOpened():
            st.error("Could not open the uploaded video.")
        else:
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            progress_bar = st.progress(0)
            status = st.empty()
            frame_number = 0

            # Process frames with YOLOv8 + ByteTrack
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                results = model.track(
                    frame,
                    conf=confidence,
                    imgsz=image_size,
                    tracker="bytetrack.yaml",
                    persist=True,
                    verbose=False
                )

                annotated_frame = results[0].plot()
                writer.write(annotated_frame)

                frame_number += 1
                if total_frames > 0:
                    progress = frame_number / total_frames
                    progress_bar.progress(progress)
                    status.write(f"Processing frame {frame_number}/{total_frames}")

            cap.release()
            writer.release()
            progress_bar.progress(1.0)
            status.success("✅ Pothole detection completed!")

            # Display result
            st.subheader("📊 Detected Output")

            with open(output_path, "rb") as video_file:
                video_bytes = video_file.read()

            st.video(video_bytes)

            st.download_button(
                label="⬇️ Download Annotated Video",
                data=video_bytes,
                file_name="drishti_pothole_detection.mp4",
                mime="video/mp4"
            )

        # Cleanup temp input
        if os.path.exists(input_path):
            os.remove(input_path)

else:
    st.info("👆 Upload a road or dashcam video above to begin analysis.")
    st.markdown("""
    **What this model detects:**
    - 🕳️ Potholes & road craters (with depth estimation cues)
    - 🛣️ Asphalt raveling & surface distress
    - 💧 Waterlogged depressions
    - ⚠️ Edge deterioration and shoulder failures
    """)