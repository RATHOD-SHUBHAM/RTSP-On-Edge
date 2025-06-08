#!/usr/bin/env python3
import sys
import signal

import pyrealsense2 as rs
import numpy as np

from gi.repository import Gst, GstRtspServer, GObject, GLib

# --------------------------------------------------------------------------------
#  RealSenseCapture: wraps a RealSense pipeline that returns color frames as NumPy arrays
# --------------------------------------------------------------------------------
class RealSenseCapture:
    def __init__(self):
        # Configure RealSense to stream color only at 640×480 @ 30 FPS
        self.pipeline = rs.pipeline()
        cfg = rs.config()
        cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(cfg)

    def get_frame(self):
        # Wait for the next set of frames, get color, convert to NumPy
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            return None
        color_image = np.asanyarray(color_frame.get_data())
        return color_image

    def __del__(self):
        # Ensure the pipeline is stopped on deletion
        try:
            self.pipeline.stop()
        except:
            pass


# --------------------------------------------------------------------------------
#  RealSenseMediaFactory: a GstRtspServer factory that pushes RealSense frames into appsrc
# --------------------------------------------------------------------------------
class RealSenseMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, **properties):
        super(RealSenseMediaFactory, self).__init__(**properties)
        # Instantiate our RealSenseCapture backend
        self.capture = RealSenseCapture()
        self.number_frames = 0
        # Duration of a single buffer (in nanoseconds). 30 FPS => ~33333333 ns
        self.duration = int(1e9 / 30)

        # GStreamer pipeline string:
        #  - appsrc named "source", live, time format
        #  - caps: BGR, 640×480, 30 fps
        #  - videoconvert to I420
        #  - x264enc with zerolatency
        #  - rtph264pay payloader named "pay0" for RTSP
        self.launch_string = (
            "( appsrc name=source is-live=true block=true format=time "
            "caps=video/x-raw,format=BGR,width=640,height=480,framerate=30/1 "
            "! videoconvert "
            "! video/x-raw,format=I420 "
            "! x264enc tune=zerolatency speed-preset=ultrafast "
            "! rtph264pay name=pay0 pt=96 )"
        )

    def do_create_element(self, url):
        # Parse the launch string into a Gst.Element
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        # Called once the media is constructed; find our appsrc and attach "need-data"
        appsrc = rtsp_media.get_element().get_child_by_name("source")
        appsrc.connect("need-data", self.on_need_data)

    def on_need_data(self, src, length):
        # Called whenever GStreamer wants more data in appsrc
        frame = self.capture.get_frame()
        if frame is None:
            return

        data = frame.tobytes()
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)

        # Timestamp in nanoseconds
        timestamp = self.number_frames * self.duration
        buf.pts = buf.dts = int(timestamp)
        buf.duration = self.duration
        buf.offset = self.number_frames
        self.number_frames += 1

        # Push the buffer downstream
        src.emit("push-buffer", buf)


# --------------------------------------------------------------------------------
#  Main: sets up the RTSP server and attaches our factory at /test
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    # Initialize GObject threading and GStreamer
    GObject.threads_init()
    Gst.init(None)

    # Create the RTSP server
    server = GstRtspServer.RTSPServer()
    server.set_service("8554")  # default RTSP port; can be changed if needed

    # Create and configure our media factory
    factory = RealSenseMediaFactory()
    factory.set_shared(True)

    # Mount it at /test
    mounts = server.get_mount_points()
    mounts.add_factory("/test", factory)

    # Start the server
    server.attach(None)

    print("📡 RTSP server is live at rtsp://<JETSON_IP>:8554/test")
    print("   (Press Ctrl+C to stop)")

    # Handle Ctrl+C gracefully
    def _signal_handler(sig, frame):
        print("\nStopping RTSP server...")
        GLib.MainLoop().quit()

    signal.signal(signal.SIGINT, _signal_handler)

    # Run the GLib main loop so the server stays alive
    loop = GLib.MainLoop()
    loop.run()


# ffplay rtsp://192.168.169.219:8554/test
