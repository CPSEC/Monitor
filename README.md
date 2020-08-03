# Monitor
Debugging tool for our testbed.

## Installation
```cmd
pip install PyQt5
pip install PyQt5-tools
pip install pyqtgraph
pip install pandas
pip install opencv-python
pip install scipy
```

## Run 
```cmd
python Monitor.py
```

## Test
1. start listening
2. start recording
3. run test client
```cmd
python test/client.py
```

## Data Format
test/data_sample.py

## Key Features
* plot sensor data
* start/stop tcp listening
* start/stop data recording
* live camera video show
* save/open csv file
* reset data received
