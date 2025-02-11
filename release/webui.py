from flask import Flask, Response, render_template
import cv2
import numpy as np
import mss
import threading
import soundcard as sc
import struct
import time

app = Flask(__name__)
MONITOR = {"top": 0, "left": 0, "width": 1920, "height": 1080}
capture_flag = threading.Event()
capture_flag.set()
lock = threading.Lock()

def generate_frames():
    """Capture the screen and yield JPEG-encoded frames."""
    with mss.mss() as sct:
        while capture_flag.is_set():
            frame = np.array(sct.grab(MONITOR))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
            time.sleep(0.03)  # ~30 FPS

CHUNK = 1024  # Frames per chunk
SAMPLE_RATE = 44100  # Sample rate
CHANNELS = 2  # Stereo

def wav_header(sample_rate, num_channels):
    """Generate a WAV header with dynamic channels."""
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_chunk_size = 0x7FFFFFFF  # Large dummy size for streaming
    riff_chunk_size = data_chunk_size + 36

    header = struct.pack('<4sI4s4sIHHIIHH4sI',
                         b'RIFF', riff_chunk_size, b'WAVE',
                         b'fmt ', 16, 1, num_channels,
                         sample_rate, byte_rate, block_align,
                         bits_per_sample, b'data', data_chunk_size)
    return header

def generate_audio():
    """Capture loopback audio and stream as WAV."""
    try:
        default_speaker = sc.default_speaker()
        mic = sc.get_microphone(id=default_speaker.id, include_loopback=True)

        with mic.recorder(samplerate=SAMPLE_RATE, channels=CHANNELS) as recorder:
            yield wav_header(SAMPLE_RATE, CHANNELS)  # Send WAV header

            while capture_flag.is_set():
                data = recorder.record(numframes=CHUNK)
                data_int16 = (data * 32767).astype(np.int16)
                yield data_int16.tobytes()
    except Exception as e:
        print(f"Audio Error: {e}")

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/audio_feed")
def audio_feed():
    return Response(generate_audio(), mimetype="audio/wav")

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/stop")
def stop():
    """Stop screen and audio capture."""
    global capture_flag
    with lock:
        capture_flag.clear()
    return "Capture stopped."

@app.route("/start")
def start():
    """Start screen and audio capture."""
    global capture_flag
    with lock:
        if not capture_flag.is_set():
            capture_flag.set()
    return "Capture started."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
