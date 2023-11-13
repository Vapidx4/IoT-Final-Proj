# import pandas as pd
from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq
import RPi.GPIO as GPIO
import libs.DHT as DHT
import libs.emailSender as EmailSender

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

dht_pin = 11 
dht = DHT.DHT(dht_pin)

en = 29
fan1 = 13
fan2 = 15
GPIO.setup(en, GPIO.OUT)
GPIO.setup(fan1, GPIO.OUT)
GPIO.setup(fan2, GPIO.OUT)

# Initial temperature values
temp = 28
humidity = 0
light_on = False
email_sent = False
wait_time = 300

GPIO.output(en, GPIO.LOW)

# while True:
#     GPIO.output(en, GPIO.LOW)
#     GPIO.output(fan1, GPIO.LOW)
#     GPIO.output(fan2, GPIO.HIGH)

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
    if not email_sent and n % (wait_time / 5) == 0 and temp >= 24:
        fan_on = EmailSender.main(temp)
        email_sent = True

    # Enables fan based on fan status
    print(f"Setting fan status: {fan_on}")
    GPIO.output(en, GPIO.HIGH if fan_on else GPIO.LOW)
    GPIO.output(fan1, GPIO.LOW if fan_on else GPIO.HIGH)
    GPIO.output(fan2, GPIO.HIGH if fan_on else GPIO.LOW)


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

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)