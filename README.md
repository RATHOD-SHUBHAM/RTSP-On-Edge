# 📡 RTSP-on-Edge: Real-Time Camera Streaming from Jetson & Raspberry Pi

Welcome to **RTSP-on-Edge**, a lightweight Python-based solution for real-time camera streaming from edge devices like **Raspberry Pi** and **NVIDIA Jetson AGX**.

Whether you're working on robotics, remote monitoring, or AI-based vision systems, this project helps you stream your camera feed over **RTSP** using **GStreamer**, with optional global access using **ngrok**.

---

Stream live camera feeds from **NVIDIA Jetson** or **Raspberry Pi** over **RTSP** using GStreamer and Python.  
Ideal for robotics, IoT, computer vision, and edge AI applications where real-time video access is critical.

---

## 🧠 Why This Project?

Real-time video is essential for edge devices in applications like:
- 🤖 Robotics navigation and teleoperation
- 🧠 Generative AI agents with vision inputs
- 🌱 Remote monitoring in agriculture, industry, or research
- 📦 Visual inspection pipelines in edge ML setups

This repo lets you:
- Capture video using Intel RealSense (Jetson) or USB webcams (Pi)
- Stream over RTSP using a lightweight GStreamer pipeline
- Expose feeds locally or globally via ngrok or port forwarding

---

## 🚀 Features

- 🔧 Built-in GStreamer RTSP server in Python (`GstRtspServer`)
- ✅ Works with `/dev/video0` or RealSense RGB stream
- 🧩 Compatible with JetPack 6.x and Raspberry Pi OS
- 🌍 Easily make streams accessible online via [ngrok](https://ngrok.com)

---

## 📂 Project Structure
```
├── pi_rts_protocol/ # RTSP stream using RaspberryPI
│ └── README.md # Setup and usage instructions
│
├── jetson_realSense/ # RTSP stream using Intel RealSense (Jetson)
│ └── LinkedIn blog attached below
│
└── README.md # This file
```


---

---

## 🚀 Quick Start

### 1. Raspberry Pi (`pi_rts_protocol/`)

Use this folder if you want to stream from a USB webcam on a Raspberry Pi (e.g., `/dev/video0`). It includes a Python script (`logi.py`) and its own detailed `README.md` with steps to install dependencies and run the server.

👉 [**Go to Pi RTSP Setup →**](./pi_rts_protocol/README.md)

---

### 2. NVIDIA Jetson AGX Xavier (`jetsonrealSense/`)

Use this folder if you're working with an Intel RealSense D435i camera on Jetson AGX running JetPack 6.

The integration process requires specific kernel patches, RealSense driver builds, and RTSP setup. All steps and troubleshooting details are documented in this blog post:

🔗 [**Read the Jetson Setup Guide on LinkedIn →**](https://www.linkedin.com/pulse/realsense-jetpack-6-complete-guide-rtsp-gstreamer-ngrok-shankar-aalqc/?trackingId=iF9%2B%2F%2Bi9SOmE5ifZmypiyQ%3D%3D)
---

## 🌐 Accessing the RTSP Stream Globally

Both scripts can be extended to support public streaming using **ngrok**:

```
./ngrok tcp 8554
```
Then stream using:
```
ffplay -rtsp_transport tcp rtsp://<ngrok-address>:<port>/camera
```
