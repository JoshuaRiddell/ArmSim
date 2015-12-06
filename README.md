# ArmSim
## 6DOF robotic arm movement sequener

### About
Version: V0.1

Developed under Windows 7, Python 3.4.2

ArmSim is an interface which allows quick and simple movement sequencing of
complex robotic arms. It currently supports the 6DOF robotic arm found at
http://www.thingiverse.com/thing:30163.

### Main Application

#### Installation

1. Install all external resources see [Dependencies](https://github.com/JoshuaRiddell/ArnSim/blob/pyglet-legacy/README.md#Dependencies).

2. Execute ./build/main.py in Python3.

#### Troubleshooting

* If simulation window graphics look weird (black stripes or bad lighting):
  * open to ./conifg/simulation, change 'force_no_multisampling' to 1 and restart the program

* If simulation window does not pan when holding shift:
  * run ./conifg/hid_set.py, and get the int value for when your shift key is pressed.
    Then, in ./conifg/simulation change the value of 'shift' to the new value for your system.

### Raspberry Pi

#### Installation

1. Install pigpio: http://abyz.co.uk/rpi/pigpio/download.html

2. Edit servo_poi to suit your pin configuration and servo types (pulses are in
    the standard milliseconds). ./raspberry_pi/setServo.py is what I used to
    get endpoints, it may help to use and edit this for your system if it is
    similar to mine.

3. Edit HOST and PORT ./raspberry_pi/network_listen.py to suit your current
    network configuration. If you change the port, then this must also be
    changed in ./build/server.py

4. Transfer ./raspberry_pi/ to your RPi.

5. Execute ./raspberry_pi/network_listen.py. Now the checkbox in the main
    applet will connect to your RPi!

#### Troubleshooting

* if network_listen.py is instantly crashing:
  * check you have the pigpio daemon running
  * check your ip
  * check your port is not in use

### Dependencies

* Pyglet - http://www.pyglet.org/download.html
  * Windows:    Download the relevant wheel from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/) and use pip
                to install
  * Unix:       pip install pyglet

* pyglet_gui - https://github.com/jorgecarleitao/pyglet-gui
  * Windows and Unix:
          pip install git+https://github.com/jorgecarleitao/pyglet-gui.git

* pyglet_obj - https://github.com/reidrac/pyglet-obj-batch
    (included in ArmSim package, here for credit)
