from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq
import RPi.GPIO as GPIO
import libs.DHT as DHT
import libs.emailSender as EmailSender
import paho.mqtt.client as mqtt
import sqlite3
import binascii
import bluetooth


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

led = 37
GPIO.setup(led, GPIO.OUT)
GPIO.output(led, GPIO.LOW)

dht_pin = 40 
dht = DHT.DHT(dht_pin)
en = 29
fan1 = 31
fan2 = 33
GPIO.setup(en, GPIO.OUT)
GPIO.setup(fan1, GPIO.OUT)
GPIO.setup(fan2, GPIO.OUT)

mqtt_broker = "192.168.7.48"
mqtt_port = 1883
mqtt_topic_light = "Home/LIGHT"
mqtt_topic_user = "Home/USER"


temp = 28
humidity = 0
light_on = False
fan_on = False
light_email_sent = False
fan_email_sent = False
user_email_sent = False
email_sent = False
wait_time = 300
GPIO.output(en, GPIO.LOW)

u_id = '73fc5ea0'
light_intensity = 1024
light_threshold = 400

rssi_threshold = -80
#light_on = False
#email_sent = False
#wait_time = 300

def discover_devices():
    nearby_devices = bluetooth.discover_devices(duration=1)
    return nearby_devices

def get_device_count(threshold=0): 
    nearby_devices = discover_devices()
    return len(nearby_devices)


# print(f"Found {get_device_count(rssi_threshold)} nearby Bluetooth device(s):")


connection = sqlite3.connect(database='db.sql')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        user_id TEXT PRIMARY KEY,
        user_name TEXT NOT NULL,
        temp_threshold FLOAT NOT NULL,
        humidity_threshold FLOAT NOT NULL,
        light_threshold INTEGER NOT NULL,
        rssi_threshold INTEGER NOT NULL
    )
''')

# Commit the changes
connection.commit()

insert_data_query = '''
    INSERT OR IGNORE INTO settings (user_id, user_name, temp_threshold, humidity_threshold, light_threshold, rssi_threshold)
    VALUES 
        ('AC 85 23 E1', 'Brandon', 25.0, 60.0, 400, -80),
        ('cc8523e1', 'Evan', 20.5, 55.0, 300, -50),
        ('73fc5ea0', 'Phuc', 22.0, 65.0, 600, -40);
'''

cursor.executescript(insert_data_query)

# Commit the changes
connection.commit()


# cursor.close()
# connection.close()

user_details_query = connection.execute(f"SELECT user_name, temp_threshold, humidity_threshold, light_threshold FROM settings WHERE user_id = '{u_id}'")
user_details = user_details_query.fetchone()
user_name, temp_threshold, humidity_threshold, light_threshold = user_details

cursor.close()
connection.close()


    

# hex_string = binascii.hexlify(b'\xcc\x85#\xe1').decode('utf-8')
# print(hex_string)





# MQTT callback function
def on_message(client, userdata, msg):
    global light_intensity, u_id
    try:
        if msg.topic == mqtt_topic_light:
            light_intensity = int(msg.payload)
            # print(f"Received message on topic {msg.topic}: {light_intensity}")
        elif msg.topic == mqtt_topic_user:
            global u_id 
            u_id = binascii.hexlify(msg.payload).decode('utf-8')
            EmailSender.send_email_user(user_name)
            print(f"Received message on topic {msg.topic}: {u_id}")
            print(type(u_id))
            # print("Raw payload:", msg.payload)
        else:
            print(f"Received message on unknown topic {msg.topic}")

    except ValueError as e:
        print(f"Error parsing MQTT message: {e}")




# MQTT client setup
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.subscribe(mqtt_topic_light)
mqtt_client.subscribe(mqtt_topic_user)

# Start the MQTT client loop in a separate thread
mqtt_client.loop_start()

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

light_button =  html.Div([
    daq.ToggleSwitch(
        id='light-button',
        value=light_on,
        vertical=True

    ),
])

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
                                        html.H3(f"User: {user_name}"),
                                        html.Ul(
                                            children=[
                                                html.Li(f"User: {user_name}"),
                                                html.Li(f"Temperature Threshold: {temp_threshold} °C"),
                                                html.Li(f"Humidity Threshold: {humidity_threshold} %"),
                                                html.Li(f"Light Threshold: {light_threshold} Lumens"),
                                            ]
                                        )
                                    ]
                                ),
                                html.Div(
                                    className="block",
                                    children=[
                                        html.H3(f"Fan Status: {fan_on}"),
                                        html.Img(className="block", src=f"assets/img/{'fan/on' if fan_on else 'fan/off'}.png")
                                    ]
                                ),
                                html.Div(
                                    className="block",
                                    children=[
                                        html.H3(f"Light Status: {'on' if light_on else 'off'}"),
                                        light_button,

                                        html.Img(className="block", src=f"assets/img/{'light/on' if light_on else 'light/off'}.png", style={"height": "100px", "width": "100px"})
                                    ]
                                ),
                                 html.Div(
                                    className="block",
                                    children=[
                                        html.H3(f"Nearby Bluetooth Devices: {get_device_count()}"),
                                        html.Img(className="block", src=f"assets/img/Bluetooth.png", style={"height": "100px", "width": "100px"})

                                        ]
                                )
                                
                            ]
                        )
                    ]
                ),
                # Adds Interval component to trigger the callback every 5 seconds
                dcc.Interval(
                    id='interval-component',
                    interval=5 * 500,  # in milliseconds
                    n_intervals=0
                )
            ]
        ),
    ]
)        


# Check for email response every 5 seconds
@app.callback(
    Output('main-content', 'children'),
    [Input('interval-component', 'n_intervals'), Input('light-button', 'value')]
)
def update(n, light_status):
    global bt_devices, light_on, fan_on, email_sent, light_email_sent, user_email_sent, fan_email_sent, wait_time, temp, humidity, light_intensity, u_id, light_threshold, humidity_threshold, temp_threshold, rssi_threshold

    # print('Updating...')
    # print(light_intensity)
    connection = sqlite3.connect(database='db.sql')
    cursor = connection.cursor()
    
    user_details_query = connection.execute(f"SELECT user_name, temp_threshold, humidity_threshold, light_threshold FROM settings WHERE user_id = '{u_id}'")
    user_details = user_details_query.fetchone()
    user_name, temp_threshold, humidity_threshold, light_threshold = user_details

    cursor.close()
    connection.close()
    
    # print(u_id)
    # print(user_name)
    
    light_on = light_status


    # Check for email response
    if not light_email_sent and light_intensity >= light_threshold:
        print(f"Treshold of {light_threshold} reached... Sending email")
        light_on = EmailSender.send_email_light(light_intensity)
        GPIO.output(led, GPIO.HIGH)   # turn light on
        light_email_sent = True
        email_sent = True
        
    if not fan_email_sent and n % (wait_time / 5) == 0 and temp >= temp_threshold:
        fan_on = EmailSender.send_email_fan(temp)
        fan_email_sent = True
        email_sent = True


    # Enables fan based on fan status
    # print(f"Setting fan status: {fan_on}")
    GPIO.output(en, GPIO.HIGH if fan_on else GPIO.LOW)
    GPIO.output(fan1, GPIO.LOW if fan_on else GPIO.HIGH)
    GPIO.output(fan2, GPIO.HIGH if fan_on else GPIO.LOW)

    # Control the light based on the threshold
    if light_intensity <= light_threshold:
        GPIO.output(led, GPIO.HIGH)   # turn light on
        light_on = True
        light_email_sent = True

    else:
        GPIO.output(led, GPIO.LOW)   # turn light off
        light_on = False
        light_email_sent = False
        
    # if temp

    content = [
        gauge("Temperature", "Celsius", -50, 50, temp),
        gauge("Humidity", "%", 0, 100, humidity),
        gauge("Light Intensity", "Lumens", 0, 1024, light_intensity),

        html.Div(
            className="col-right",
            children=[
                html.Div(
                    className="block",
                        children=[
                            html.H3(f"User: {user_name}"),
                            html.Ul(
                                children=[
                                    html.Li(f"User: {user_name}"),
                                    html.Li(f"Temperature Threshold: {temp_threshold} °C"),
                                    html.Li(f"Humidity Threshold: {humidity_threshold} %"),
                                    html.Li(f"Light Threshold: {light_threshold} Lumens"),
                                ]
                            )
                        ]
                    ),
                html.Div(
                    className="block",
                    children=[
                        html.H3(f"Fan Status: {'on' if fan_on else 'off'}"),
                        html.Img(className="block", src=f"assets/img/{'fan/on' if fan_on else 'fan/off'}.png")
                    ]
                ),
                html.Div(
                    className="block",
                    children=[
                        html.H3(f"Light Status: {'on' if light_on else 'off'}"),
                        light_button,

                        html.Img(className="block", src=f"assets/img/{'light/on' if light_on else 'light/off'}.png", style={"height": "100px", "width": "100px"})
                    ]
                ),
                html.Div(
                    className="block",
                    children=[
                        html.H3(f"Nearby Bluetooth Devices: {get_device_count()}"),
                        html.Img(className="block", src=f"assets/img/Bluetooth.png", style={"height": "100px", "width": "100px"})

                        ]
                )
                
            ]
        ),
        
    ]

    if email_sent:
        content = [
        gauge("Temperature", "Celsius", -50, 50, temp),
        gauge("Humidity", "%", 0, 100, humidity),
        gauge("Light Intensity", "Lumens", 0, 1024, light_intensity),

        html.Div(
            className="col-right",
            children=[
                html.Div(
                        className="block",
                        children=[
                            html.P(f"A notification has been sent to your email for your smart home")
                        ]
                    ),
                html.Div(
                        className="block",
                        children=[
                            html.H3(f"User: {user_name}"),
                            html.Ul(
                                children=[
                                    html.Li(f"User: {user_name}"),
                                    html.Li(f"Temperature Threshold: {temp_threshold} °C"),
                                    html.Li(f"Humidity Threshold: {humidity_threshold} %"),
                                    html.Li(f"Light Threshold: {light_threshold} Lumens"),
                                ]
                            )
                        ]
                    ),
                html.Div(
                    className="block",
                    children=[
                        html.H3(f"Fan Status: {'on' if fan_on else 'off'}"),
                        html.Img(className="block", src=f"assets/img/{'fan/on' if fan_on else 'fan/off'}.png")
                    ]
                ),
                html.Div(
                    className="block",
                    children=[
                        html.H3(f"Light Status: {'on' if light_on else 'off'}"),
                        light_button,

                        html.Img(className="block", src=f"assets/img/{'light/on' if light_on else 'light/off'}.png", style={"height": "100px", "width": "100px"})
                    ]
                ),
                html.Div(
                    className="block",
                    children=[
                        html.H3(f"Nearby Bluetooth Devices: {get_device_count()}"),
                        html.Img(className="block", src=f"assets/img/Bluetooth.png", style={"height": "100px", "width": "100px"})

                        ]
                )
            ]
        ),
    ]

    # Update layout
    return content




try:
    # Run the app
    if __name__ == '__main__':
        app.run_server(debug=True)

finally:
    # Cleanup GPIO
    GPIO.cleanup()