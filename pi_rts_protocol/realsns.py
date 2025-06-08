#!/usr/bin/env python3
import threading, queue
import numpy as np
import pyrealsense2 as rs
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

class RealSenseFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, **properties):
        super().__init__(**properties)
        self.frame_queue = queue.Queue(maxsize=10)
        self._pts = 0

        # 1. Start the RealSense pipeline in a background thread
        threading.Thread(target=self._start_realsense, daemon=True).start()

        # 2. Build a GStreamer pipeline with `appsrc` as the source
        #    We declare BGR format so that downstream `videoconvert` can handle it.
        self.launch_string = (
            'appsrc name=mysrc is-live=true format=time '
            'caps=video/x-raw,format=BGR,width=640,height=480,framerate=30/1 ! '
            'videoconvert ! '
            'x264enc speed-preset=ultrafast tune=zerolatency bitrate=800 ! '
            'rtph264pay name=pay0 pt=96 config-interval=1'
        )

    def _start_realsense(self):
        """Capture color frames from D435i and enqueue them."""
        cfg = rs.config()
        cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        pipeline = rs.pipeline()
        pipeline.start(cfg)
        try:
            while True:
                frames = pipeline.wait_for_frames()
                color = frames.get_color_frame()
                if not color:
                    continue
                img = np.asanyarray(color.get_data())
                # drop frames if queue is full
                if not self.frame_queue.full():
                    self.frame_queue.put(img)
        finally:
            pipeline.stop()

    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        appsrc = rtsp_media.get_element().get_child_by_name('mysrc')
        # Each time GStreamer needs data, `_on_need_data` is called
        appsrc.connect('need-data', self._on_need_data)

    def _on_need_data(self, src, length):
        try:
            frame = self.frame_queue.get(timeout=1)  # wait up to 1s
        except queue.Empty:
            return

        h, w, _ = frame.shape
        data = frame.tobytes()
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)
        # 1/30th of a second per frame → 30 FPS
        buf.duration = Gst.util_uint64_scale_int(1, Gst.SECOND, 30)
        buf.pts = self._pts
        self._pts += buf.duration

        src.emit('push-buffer', buf)

def main():
    Gst.init(None)
    server = GstRtspServer.RTSPServer()
    mounts = server.get_mount_points()

    factory = RealSenseFactory()
    factory.set_shared(True)
    mounts.add_factory("/camera", factory)

    server.attach(None)
    port = server.props.service
    print(f"📡 RealSense RTSP ready at rtsp://<RPI_IP>:{port}/camera")

    loop = GObject.MainLoop()
    loop.run()

if __name__ == "__main__":
    main()


"""

sudo apt update
sudo apt install -y python3-pip
pip3 install pyrealsense2 numpy


"""