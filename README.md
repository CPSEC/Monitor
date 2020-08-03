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
* parameter online adjustment, such as PID
* plot sensor data
* start/stop tcp listening
* start/stop data recording
* live camera video show
* save/open csv file
* reset data received

## Tips
There are some dependencies of operation.

If you find a button is invalid, please pay attention to your order of operation.
For example, we cannot open a csv file when receiving data; we cannot adjust PID parameters before the connection establishes.

