# IoT Smart Home Documentation

**Author:** Brandon Lee Felix  
**GitHub:** [https://github.com/Vapidx4/IoT-Final-Proj](https://github.com/Vapidx4/IoT-Final-Proj)

## Project Overview & Executive Summary

For the 2023 Fall semester project, our Internet of Things instructor, Samad, assigned me to partner up with my teammates Evan and Phuc. Our goal is to develop a smart home system. The project involves designing a dashboard that utilizes data on light, temperature, and humidity to control home lighting and fans. Furthermore, we've implemented a multi-profile system through an RFID card reader for personalized user experiences.

## Project Scopes & Objectives

### Dashboard Creation:
- Create a user-friendly dashboard that monitors and controls temperature and light.

### Sensor Integration:
- Integrate a backend that can reliably read analog data transmitted by a DHT11 and Photoresistor sensor.

### Device Control:
- Using either user or sensor inputs, activate or deactivate a smarthome end-component based on specified conditions.

### Database Integration:
- Integration of the smarthome system with a database that stores information about a user such as their id, name, and activation thresholds for fans or lights.

### RFID Profile System:
- Allows a user’s RFID card to be scanned and read by a reader, automatically logging the user in and setting their desired threshold.

### Email Integration:
- When a smarthome end component is to be activated, send an email detailing the time of activation, or ask for a permission response to activate it. Additionally, when a user logs into the system, send an email detailing their time of entry.

## Deliverables

### Deliverable 1
- Implement a digital light switch on the dashboard.

### Deliverable 2
- Integrate a DHT11 sensor to the Raspberry Pi and display temperature/humidity readings on the dashboard. Send an email when a temperature threshold is met.

### Deliverable 3
- Integrate an MQTT system using an ESP board that publishes analog readings from a photoresistor. Display readings on the dashboard and activate lights if the reading is below a defined threshold. 

### Deliverable 4
- Add functionality to the ESP board to read RFID cards. Change thresholds and display user profile information on the dashboard when an RFID card is read. Send an email when a user logs into the system.

## Requirements and Material

### Hardware
- 1 LED
- 1 Photoresistor
- 1 DHT11 Sensor
- Dupont cables
- Potentiometer
- RFID Card Reader
- 3 RFID Cards
- ESP8266 Board
- Raspberry Pi
- 1 DC Motor
- 1 Motor Driver IC

### Software
- Mosquitto MQTT
- Wi-Fi
- Python Programming Language
- Arduino IDE
- Visual Studio Code/Pycharm (or your preferred IDE)
- SSH
- dash_daq library
- SQLite3 library
- Rpi.GPIO library
- Paho MQTT library
- Smtp library
- Ssl library
- Imaplib library
- Email library
- Datetime library
- Uuid library
- SPI.h
- MFRC522.h
- PubSubClient.h
- ESP8266WiFi.h

## Work Breakdown Structure

### Email System:
- Phuc: Develop email responses for each new feature.

### Dashboard:
- Brandon: Work on the dashboard for each implementation.

### ESP & MQTT:
- Brandon: Complete the transmission and reading of data for the MQTT system.

### Database:
- Evan: Complete the database implementation.

### LED Switch:
- Evan: Implement the switch for the first deliverable.

### Fan Control:
- Evan: Implement the fan control system.

### Photosensor & LED:
- Brandon: Implement the smart lighting system.

### RFID & User Management:
- Brandon: Complete the RFID user management system.

### Merge of Smarthome features:
- Phuc: Merge each implementation into a singular dashboard.

### General feature debugging:
- Brandon and Evan: Debug features that aren’t working as expected.

**Method and Solution**

### Dashboard Creation:
**Method:**
- Utilize Python programming language and Dash framework for creating a web-based dashboard.
- Implement dash_daq library for interactive components.

**Solution:**
- Develop a user-friendly dashboard with a digital light switch feature using buttons and LED representations.

### Sensor Integration:
**Method:**
- Read input data from DHT11 and Photoresistor using Python through the Raspberry Pi and ESP board.

**Solution:**
- Integrate DHT11 sensor readings for temperature and humidity into the dashboard.
- Implement MQTT system on an ESP board to publish photoresistor analog readings to a topic.

### Device Control:
**Method:**
- Develop inputs for activating/deactivating smart home components based on user or sensor inputs.

**Solution:**
- Activate/deactivate fans based on temperature and luminosity thresholds read by photoresistor and DHT11 sensors.

### Database Integration:
**Method:**
- Use SQLite3 library for database management in Python.

**Solution:**
- Connect the smart home system with a database for user preferences.

### RFID Profile System:
**Method:**
- Integrate RFID card reader with ESP board and MQTT system.

**Solution:**
- Read RFID cards to automatically log in users and set their desired thresholds.
- Display user profile information on the dashboard.

### Email Integration:
**Method:**
- Use Python's email library to send emails.

**Solution:**
- Send emails for component activations and user logins, asking permission for fan activation.

### ESP & MQTT:
**Method:**
- Utilize Arduino IDE for programming the ESP8266 board and Paho MQTT library for MQTT integration.

**Solution:**
- Publishes and Subscribes data through the MQTT system for communication between devices.
