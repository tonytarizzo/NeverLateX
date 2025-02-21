### NeverLateX ###

## TO DO (Hardware, Software):
------------------------------------
- ensure pen setup works correctly
- either add pen tip with cartridge or make a blunt pen tip and assemble
- add breadboard & arduino to wire stand 
- incorporate button into pen

- test increasing speeds to limit of IMU capability (general data collection speeds)
- prediction frequency, windowing method (to reach desired usability idea, online transcription)
- look into stabilo set for base training before fine-tuning
- look into using optic sensors geometry to use as threshold for when letter is writing and not writing, could be used to accuratley determine beginning and end padding?
    (the geometry I gave a basic equation in the interim report, maybe this can be utilised? And this becomes a pre-training processing step, and a at inference processing step when the model is being applied)





### Working Instructions ###
To find serial port of the arduino(mac). Then copy the address into the python script:
    
    ls /dev/tty.*               # Should look similar to "/dev/tty.usbmodem101"

The packages here are being downloade into the virutal environemnt, venv. To work with packages, first do:

    source venv/bin/activate    # Slightly different command for windows

Then you can use pip install as per usual. If new packages are installed, update the requirements.txt so we also can install them, using the command:

    pip freeze > requirements.txt  
    
To apply the arduino code, open the Arduino IDE and upload the code (first select the correct Port & Board in Tools). Then you can run the python code and they should work together as intended.



### Wiring Setup On Pen Model 2 ###
Instructions to hopefully figure out wiring.
FSRs can be wired with either pin to either voltage or ground (they are just a fancy resistor with no polarity). Therefore to test which FSR relates to which Analog Input, get the arduino running, put pressure on one FSR at a time and see which one shows a reading.
To check the optical sensors, ofc hold something close to each one individually and see if the readings change. If there is no reading in one or both sensors, check breadboard wiring is stable first, then track wiring from paper labels to the breaboard, check that that is correct (1 represents the left most wire, 4 is right most of a bundle - this orientation is looking from above at the paper label)



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
        