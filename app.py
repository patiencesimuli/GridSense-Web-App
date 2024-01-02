import flask
import serial
#import anomaly_detection_model
#import fault_classification_model
import time
from joblib import load

#Getting a list of currently connected devices and their ports
#ports = list_ports.comports()
#for port in ports: print(port)

app = flask.Flask(__name__)

# Initialize serial communication with Arduino
ser = serial.Serial('COM3', 9600)

#Reset the Arduino
ser.setDTR(False)
time.sleep(1)
ser.flushInput(1)
ser.setDTR(True)

# Global variables to store sensor data and anomaly/fault information
voltage_data = []
current_data = []
anomaly_score = None
fault_type = None

@app.route("/")
def index():
    # Retrieve and preprocess sensor data from Arduino
    global voltage_data, current_data

    while ser.in_waiting:
        line = ser.readline().decode('utf-8').strip()
        if line:
            values = line.split(',')
            voltage_data.append(float(values[0]))
            current_data.append(float(values[1]))

    # Pass sensor data to anomaly detection model
    global anomaly_score

    model_input = [voltage_data, current_data]

    #Loading the ANN detection model

    anomaly_detection_model = load('detectionANN.joblib')
    anomaly_score = anomaly_detection_model.predict(model_input)

    # If anomaly detected, pass data to fault classification model
    if anomaly_score > 0.5:
        global fault_type
        fault_classification_model = load('classANN.joblib')
        fault_type = fault_classification_model.predict(model_input)

    # Prepare data for HTML template
    data = {
        "voltage_data": voltage_data,
        "current_data": current_data,
        "anomaly_score": anomaly_score,
        "fault_type": fault_type
    }

    return flask.render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


    #PURELY ARDUINO PART THAT ONLY DISPLAYS (IN CASE OF MODEL FAILURE)
