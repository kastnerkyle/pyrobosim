sudo apt-get install python3-dev python3-numpy libsdl-dev libsdl-image1.2-dev \
libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libportmidi-dev \
libavformat-dev libswscale-dev libjpeg-dev libfreetype6-dev mercurial

hg clone https://bitbucket.org/pygame/pygame
pushd .
cd pygame
python setup.py build
python setup.py install
popd
rm -r pygame
