# import pandas as pd
from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq
import RPi.GPIO as GPIO
import libs.DHT as DHT
import libs.emailSender as EmailSender
import paho.mqtt.client as mqtt


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

mqtt_broker = "10.0.0.18"
mqtt_port = 1883
mqtt_topic = "Home/LIGHT"

# Initial temperature values
light_intensity = 28
fan_on = False
email_sent = False
wait_time = 300

# MQTT callback function
def on_message(client, userdata, msg):
    global light_intensity
    try:
        light_intensity = int(msg.payload.decode("utf-8"))
        print(f"Received message on topic {msg.topic}: {light_intensity}")
    except ValueError as e:
        print(f"Error parsing MQTT message: {e}")

# MQTT client setup
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.subscribe(mqtt_topic)

# Start the MQTT client loop in a separate thread
mqtt_client.loop_start()


external_stylesheets = [
    {
        "rel": "stylesheet",
        "href": "assets/styles.css",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.css.config.serve_locally = True

# Defines Navigation Bar
nav_bar = html.Nav(
    className="col",
    children=[
        html.H2("IoT")
    ]
)


# Defines Header
def header(title):
    return html.Header(
        children=html.H2(title)
    )


# Defines Gauge
def gauge(label, unit, minimum, maximum, val=0):
    return html.Div(
        className="block",
        children=daq.Gauge(
            showCurrentValue=True,
            color="#923E8B",
            units=unit,
            value=val,
            label=label,
            max=maximum,
            min=minimum,
        )
    )


# Define layout
app.layout = html.Div(
    className="container",
    children=[
        nav_bar,
        html.Main(
            className="col",
            children=[
                header("IoT Light Dashboard"),
                html.Div(
                    className="row",
                    id="main-content",
                    children=[
                        gauge("Light Intensity", "Units", 0, 1024, light_intensity),
                        html.Div(
                            className="col-right",
                            children=[
                                html.Div(
                                    className="block",
                                    children=[
                                        html.H3(f"Light Status: {fan_on}"),
                                        html.Img(className="block", src=f"assets/img/{'on' if fan_on else 'off'}.png")
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                # Adds Interval component to trigger the callback every 5 seconds
                dcc.Interval(
                    id='interval-component',
                    interval=5 * 1000,  # in milliseconds
                    n_intervals=0
                )
            ]
        ),
    ]
)

# Check for email response every 5 seconds
@app.callback(
    Output('main-content', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update(n):
    global fan_on, email_sent, wait_time, light_intensity

    # Check for email response
    if not email_sent and n % (wait_time / 5) == 0 and light_intensity <= 400:
        fan_on = EmailSender.main(light_intensity)
        email_sent = True


    # Update layout
    return [
        gauge("Light Intensity", "Units", 0, 1024, light_intensity),
        html.Div(
            className="col-right",
            children=[
                html.Div(
                    className="block",
                    children=[
                        html.H3(f"Light Status: {'on' if fan_on else 'off'}"),
                        html.Img(className="block", src=f"assets/img/{'on' if fan_on else 'off'}.png")
                    ]
                )
            ]
        ),
    ]

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)