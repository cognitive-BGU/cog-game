@ECHO OFF
pip install virtualenv
virtualenv venv
call .\venv\Scripts\activate
pip install numpy==1.25.1
pip install opencv-python==4.8.0.74
pip install mediapipe==0.10.2
ECHO end successfully
PAUSE

