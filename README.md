### NeverLateX ###

## TO DO:
------------------------------------
- connect optic sensor to body, add wiring inside, add fsr and imu, wire, connect all wires to arduino/breadboard, ensure works correctly
- modifiy/cleanup breadboard and data to input 3 fsr's instead of 1
- add breadboard & arduino to wire stand 
- incorporate button into pen
------------------------------------
- test increasing speeds to limit of IMU capability (general data collection speeds)
- prediction frequency, windowing method (to reach desired usability idea, online transcription)
- look into stabilo set for base training before fine-tuning




### Working Instructions ###
To find serial port of the arduino(mac). Then copy the address into the python script:
    
    ls /dev/tty.*               # Should look similar to "/dev/tty.usbmodem101"

The packages here are being downloade into the virutal environemnt, venv. To work with packages, first do:

    source venv/bin/activate    # Slightly different command for windows

Then you can use pip install as per usual. If new packages are installed, update the requirements.txt so we also can install them, using the command:

    pip freeze > requirements.txt  
    
To apply the arduino code, open the Arduino IDE and upload the code (first select the correct Port & Board in Tools). Then you can run the python code and they should work together as intended.



### Wiring Setup On Pen Model 2 ###

Orientation = Pen is pointing away from user, IMU on left surface that is up in the air

    FSR 1: The sensor located on the right surface that is up in the air. 
        - Its wires are fully seperated the whole way
        - The right node is connected to the wire with two dashes, the left node connects to the wire with one dash
    
    FSR 2: The sensor located on the left surface that is up in the air.
        - Its wires are still joined together
        - The right node is connected to the wire with two dashes, the left node connects to the wire with one dash

    FSR 3: The sensor located on the bottom surface that is not in the air.
        - Its wires are still joined together
        - The right node is connect to the wire with two dashes, the left node connects to the wire with one dash

    Optical 1: The sensor located on the left surface that is up in the air.
        - Its wires are still joined together
        - The bundle of 4 is marked by a zig zag thick line, covering all 4 wires
        - Each wire is labelled with paper labelling, persepective is from the back of the pen (looking at pins of optical)

    Optical 2: The sensor located on the right surface that is up in the air.
        - Its wires are still joined together
        - The bundle of 4 is marked by a big drawn on square (all 4 lines coloured in)
        - Each wire is labelled with paper labelling, persepective is from the back of the pen (looking at pins of optical)
        