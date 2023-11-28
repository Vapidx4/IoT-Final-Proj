from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq
import RPi.GPIO as GPIO
import libs.DHT as DHT
import libs.emailSender as EmailSender
import paho.mqtt.client as mqtt
import sqlite3

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

led = 37
GPIO.setup(led, GPIO.OUT)
GPIO.output(led, GPIO.LOW)

dht_pin = 11 
dht = DHT.DHT(dht_pin)
en = 29
fan1 = 13
fan2 = 15
GPIO.setup(en, GPIO.OUT)
GPIO.setup(fan1, GPIO.OUT)
GPIO.setup(fan2, GPIO.OUT)

mqtt_broker = "10.0.0.18"
mqtt_port = 1883
mqtt_topic = "Home/LIGHT"

temp = 28
humidity = 0
light_on = False
email_sent = False
wait_time = 300
GPIO.output(en, GPIO.LOW)

u_id = 1
light_intensity = 1024
#light_on = False
#email_sent = False
#wait_time = 300

connection = sqlite3.connect(database='db.sql')

query = connection.execute(f"SELECT light_threshold from settings where user_id = {u_id}")
light_threshold = query.fetchone()[0]

status = dht.readDHT11()
if status is dht.DHTLIB_OK:
    print("Temperature read.")
    temp = dht.temperature
    humidity = dht.humidity
    
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

def toggleFan():
    while True:
        GPIO.output(en, GPIO.HIGH)
        GPIO.output(fan1, GPIO.LOW)
        GPIO.output(fan2, GPIO.HIGH)    
        
# Define layout
app.layout = html.Div(
    className="container",
    children=[
        nav_bar,
        html.Main(
            className="col",
            children=[
                header("IoT Temperature Dashboard"),
                html.Div(
                    className="row",
                    id="main-content",
                    children=[
                        gauge("Temperature", "Celsius", -50, 50, temp),
                        gauge("Humidity", "%", 0, 100, humidity),
                        gauge("Light Intensity", "Lumens", 0, 1024, light_intensity),
                        html.Div(
                            className="col-right",
                            children=[
                                html.Div(
                                    className="block",
                                    children=[
                                        html.H3(f"Fan Status: {light_on}"),
                                        html.Img(className="block", src=f"assets/img/{'on' if light_on else 'off'}.png")
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
    global light_on, email_sent, wait_time, temp, humidity

    # Check for email response
    if not email_sent and light_intensity >= light_threshold:
        print(f"Treshold of {light_threshold} reached... Sending email")
        light_on = EmailSender.send_email(light_intensity)
        GPIO.output(led, GPIO.HIGH)   # turn light on

        email_sent = True

    # Enables fan based on fan status
    print(f"Setting fan status: {fan_on}")
    GPIO.output(en, GPIO.HIGH if fan_on else GPIO.LOW)
    GPIO.output(fan1, GPIO.LOW if fan_on else GPIO.HIGH)
    GPIO.output(fan2, GPIO.HIGH if fan_on else GPIO.LOW)

    # Control the light based on the threshold
    if light_intensity <= light_threshold:
        GPIO.output(led, GPIO.HIGH)   # turn light on

        light_on = True
        email_sent = True

    else:
        GPIO.output(led, GPIO.LOW)   # turn light off
        light_on = False
        email_sent = False

    content = [
        gauge("Temperature", "Celsius", -50, 50, temp),
        gauge("Humidity", "%", 0, 100, humidity),
        html.Div(
            className="col-right",
            children=[
                html.Div(
                    className="block",
                    children=[
                        html.H3(f"Fan Status: {'on' if fan_on else 'off'}"),
                        html.Img(className="block", src=f"assets/img/{'on' if fan_on else 'off'}.png")
                    ]
                )
            ]
        ),
        gauge("Light Intensity", "Units", 0, 1024, light_intensity),
        html.Div(
            className="col-right",
            children=[
                html.Div(
                    className="block",
                    children=[
                        html.H3(f"Light Status: {'on' if light_on else 'off'}"),

                        html.Img(className="block", src=f"assets/img/{'on' if light_on else 'off'}.png", style={"height": "100px", "width": "100px"})
                    ]
                )
            ]
        ),
    ]

    if email_sent:
        content = [
        gauge("Temperature", "Celsius", -50, 50, temp),
        gauge("Humidity", "%", 0, 100, humidity),
        html.Div(
            className="col-right",
            children=[
                html.Div(
                        className="block",
                        children=[
                            html.P("A notification has been sent to your email")
                        ]
                    ),
                html.Div(
                    className="block",
                    children=[
                        html.H3(f"Fan Status: {'on' if fan_on else 'off'}"),
                        html.Img(className="block", src=f"assets/img/{'on' if fan_on else 'off'}.png")
                    ]
                )
            ]
        ),
    ]

    # Update layout
    return content

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

try:
    # Run the app
    if __name__ == '__main__':
        app.run_server(debug=True)

finally:
    # Cleanup GPIO
    GPIO.cleanup()