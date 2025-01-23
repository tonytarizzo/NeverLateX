### NeverLateX ###

## TO DO:
- fix glitchy button - DONE
- change updating csv to update a dataframe instead, and at end update csv or periodically
- test increasing speeds to limit of IMU capability
- create a system of displaying a label, button is clicked to begin recording, label is drawn, button is pressed, new label is shown and waits for button to be pressed for new recording - and for all of this to be uploaded to csv correctly.
- once this is done, create small initial test dataset and train demo model on this
- figure out how to incorporate model.predict into the python script and output letters when categorised


### Working Instructions ###
To find serial port of the arduino(mac). Then copy the address into the python script:
    
    ls /dev/tty.*               # Should look similar to "/dev/tty.usbmodem101"

The packages here are being downloade into the virutal environemnt, venv. To work with packages, first do:

    source venv/bin/activate    # Slightly different command for windows

Then you can use pip install as per usual. If new packages are installed, update the requirements.txt so we also can install them, using the command:

    pip freeze > requirements.txt  
    
To apply the arduino code, open the Arduino IDE and upload the code (first select the correct Port & Board in Tools). Then you can run the python code and they should work together as intended.