#!/usr/bin/env python3
import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

class CameraFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, **properties):
        super().__init__(**properties)
        # Launch pipeline: capture from /dev/video0, convert, encode H.264, RTP‐pack
        self.launch_string = (
            'v4l2src device=/dev/video0 ! '
            'video/x-raw,framerate=30/1,width=640,height=480 ! '
            'videoconvert ! '
            'x264enc speed-preset=ultrafast tune=zerolatency bitrate=800 ! '
            'rtph264pay name=pay0 pt=96 config-interval=1'
        )

    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        pass  # you can hook into media config here if needed

def main():
    Gst.init(None)
    server = GstRtspServer.RTSPServer()
    mounts = server.get_mount_points()

    factory = CameraFactory()
    factory.set_shared(True)  # multiple clients can connect
    mounts.add_factory("/camera", factory)

    server.attach(None)
    ip = "0.0.0.0"
    port = server.props.service  # default is "8554"
    print(f"📡 RTSP stream ready at rtsp://<RPI_IP>:{port}/camera")
    
    loop = GObject.MainLoop()
    loop.run()

if __name__ == "__main__":
    main()


# 192.168.169.66
# rtsp://192.168.169.66:8554/camera
