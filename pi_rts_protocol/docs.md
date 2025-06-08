### Steps to install 
1. Install System Dependencies

sudo apt update

sudo apt install -y \
  python3-gi python3-gst-1.0 gir1.2-gst-rtsp-server-1.0 \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-libav

'''
python3-gi / python3-gst-1.0: Python GObject introspection for GStreamer

gir1.2-gst-rtsp-server-1.0: GStreamer RTSP server bindings

gstreamer1.0-plugins-*: needed for V4L2, encoding, RTP, etc.
'''

2. Install requirements.txt
'''
pycairo==1.28.0
PyGObject==3.46.0
'''

### Code Logic
What it does:

  * v4l2src grabs frames from /dev/video0.

  * videoconvert ensures format compatibility.

  * x264enc encodes into H.264 (ultrafast + zerolatency for low latency).

  * rtph264pay packetizes into RTP.

  * GStreamer’s RTSP server mounts it at /camera.


## Run
simply run:
  python3 logi.py

and it should start up, printing something like:

📡 RTSP stream ready at rtsp://<your-pi-ip>:8554/camera 


### Check IP
Terminal
  hostname -I

This will print your Pi’s IP address(es), e.g. 192.168.1.42

## This is our Raspberry Pi IP
  192.168.169.66

So RTSP stream will be available at
  rtsp://192.168.169.66:8554/camera


#### --------------------------------------------------------------------------------- ####
#### The previous commands will run locally

#### Now to stream it outside network, we need to perform port forwarding

### For portforwarding we use ngrok

Step 1: Install the ngrok Agent
To download and install the ngrok agent on your remote Raspberry Pi device, follow these steps:

  Open a terminal into your remote Raspberry Pi device.
    * wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz

  Unzip the downloaded file and move it to a directory in your PATH. Below is an example for /usr/local/bin:
    * sudo tar xvzf ./ngrok-v3-stable-linux-arm64.tgz -C /usr/local/bin

  Verify installation
    * ngrok version
  You should see output like:
    * ngrok version 3.x.x


  Now that you have installed ngrok on your Raspberry Pi device, link it to your ngrok account by using your authtoken:
    * ngrok authtoken NGROK_AUTHTOKEN
Note: Replace NGROK_AUTHTOKEN with your unique ngrok authtoken found in the ngrok dashboard.
I have used my authtoken


#### Running ngrok
  >> ngrok tcp 8554

It will output something like this:
ngrok                                                           (Ctrl+C to quit)
                                                                                
🛡️ Protect endpoints w/ IP Intelligence: https://ngrok.com/r/ipintel             
                                                                                
Session Status                online                                            
Account                       Rayan (Plan: Free)                                
Version                       3.22.1                                            
Region                        United States (us)                                
Web Interface                 http://127.0.0.1:4040                             
Forwarding                    tcp://0.tcp.ngrok.io:14800 -> localhost:8554      
                                                                                
Connections                   ttl     opn     rt1     rt5     p50     p90       
                              0       0       0.00    0.00    0.00    0.00     


# Running Application
Keep both processes running on your Pi:

## Terminal One
>> cd /home/pi/Documents/rts_protocol
Activate the venv
>> source /home/pi/Documents/rts_protocol/rts/bin/activate
Then
1. Your Python RTSP server: 
    python3 logi.py


## Terminal Two
2. The ngrok tunnel: 
    ngrok tcp 8554

Give you use this exact URL in VLC (or ffplay, OpenCV, VSS, etc.):
  rtsp://0.tcp.ngrok.io:19524/camera  ### This should be same as the one ngrok publishesh

### VLC
  On your friend’s machine in VLC

  Media → Open Network Stream…

  Paste rtsp://0.tcp.ngrok.io:19524/camera

  Click Play

  

