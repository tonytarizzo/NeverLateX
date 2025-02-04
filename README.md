### NeverLateX ###

## TO DO:
- test increasing speeds to limit of IMU capability
- write a separate script for only prediction
- collect new set of data with the IMU + force setup 
- retrain the model with new set of sensor inputs 
- add optic sensors to circuit (figure out connections)


### Working Instructions ###
To find serial port of the arduino(mac). Then copy the address into the python script:
    
    ls /dev/tty.*               # Should look similar to "/dev/tty.usbmodem101"

The packages here are being downloade into the virutal environemnt, venv. To work with packages, first do:

    source venv/bin/activate    # Slightly different command for windows

Then you can use pip install as per usual. If new packages are installed, update the requirements.txt so we also can install them, using the command:

    pip freeze > requirements.txt  
    
To apply the arduino code, open the Arduino IDE and upload the code (first select the correct Port & Board in Tools). Then you can run the python code and they should work together as intended.