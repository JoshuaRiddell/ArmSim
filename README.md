# ArmSim
## Generalised Robotic Arm Visualiser and Sequencer

### About
Developed under Windows 7, Python 3.4.2; V0.1

ArmSim is an interface which allows quick and simple movement sequencing of
complex robotic arms. It currently supports any robotic arm with chained
rotational joints, i.e., linear actuators and non-rigid joints are currently
not supported.

This was originally created for Assignment 3 of CSSE1001 at UQ in semester 1, 2015.

The master branch is currently partially functional - to see the state of the assignment as it was handed in please see the ['pyglet-legacy'](https://github.com/JoshuaRiddell/ArmSim/tree/pyglet-legacy) branch.

### Main Application

#### Installation

1. Install all external resources see [Dependencies](https://github.com/JoshuaRiddell/ArmSim#dependencies).

2. Execute ./build/main.py in Python3.

### Dependencies

* [PyQt4](http://pyqt.sourceforge.net/Docs/PyQt4/): pip install PyQt4
* [Numpy](http://www.numpy.org): pip install numpy
