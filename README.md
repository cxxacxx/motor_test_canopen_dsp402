# motor_test_canopen_dsp402
ZeroerrServo motor test program, may also be useful for other canopen motors

This program relies on USBCAN-I Pro (广成科技单通道CAN总线分析仪http://www1.gcanbox.com/yhsc/USBCAN-IPro.pdf).

This program should only be running on Windows, because it relies on a Windows dll file. Before using this program, users should install ecanvci 1.1.3 (https://pypi.org/project/ecanvci/)

pip install ecanvci

Users can test the profile position mode, interpolation position mode, profile velocity mode, and profile torque mode using this program.
