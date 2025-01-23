# NeverLateX

To find serial port of the arduino(mac). Then copy the address into the python script:
    
    ls /dev/tty.*               # Should look similar to "/dev/tty.usbmodem101"

To interact with the arduino from vsc and terminal, download Arduino extension and install system level package:

    brew install arduino-cli    # System level download
    arduino-cli version         # To verify correct installation
    
    Then in VSC settings, look up arduino.path, 




