#!/usr/bin/env python

import requests
import time
import sys
from datetime import datetime, timedelta
import os

# Idea and details located here. I just added SMS capability
# https://packetlife.net/blog/2019/aug/7/apis-real-life-snagging-global-entry-interview/


# API URL
APPOINTMENTS_URL = "https://ttp.cbp.dhs.gov/schedulerapi/slots?orderBy=soonest&limit=1&locationId={}&minimum=1"

# List of Global Entry locations
LOCATION_IDS = {
    'ATL': 1704
}

# How often to run this check in seconds
TIME_WAIT = 3600

# Number of days into the future to look for appointments
DAYS_OUT = 120

# PUSHOVER
PUSHOVER_USER_KEY = os.environ['PUSHOVER_USER_KEY']
PUSHOVER_TOKEN_KEY = os.environ['PUSHOVER_TOKEN_KEY']

# Dates
now = datetime.now()
future_date = now + timedelta(days=DAYS_OUT)

def check_appointments(city, id):
    url = APPOINTMENTS_URL.format(id)
    appointments = requests.get(url).json()
    return appointments

def appointment_in_timeframe(now, future_date, appointment_date):
    if now <= appt_datetime <= future_date:
        return True
    else:
        return False

def send_pushover(message: str):
    data = {
        "token": PUSHOVER_TOKEN_KEY,
        "user": PUSHOVER_USER_KEY,
        "device": os.environ['PUSHOVER_DEVICE'],
        "title": "Global Entry Appointment Found!",
        "message" : message,
    }
    return requests.post("https://api.pushover.net/1/messages.json", data=data)


try:
    send_pushover("starting script")
    while True:
        for city, id in LOCATION_IDS.items():
            try:
                appointments = check_appointments(city, id)
            except Exception as e:
                print("Could not retrieve appointments from API.")
                appointments = []
            if appointments:
                appt_datetime = datetime.strptime(appointments[0]['startTimestamp'], '%Y-%m-%dT%H:%M')
                if appointment_in_timeframe(now, future_date, appt_datetime):
                    message = "{}: Found an appointment at {}!".format(city, appointments[0]['startTimestamp'])
                    try:
                        res = send_pushover(message)
                        print(message, "Sent text successfully! {}".format(res.status_code))
                    except Exception as e:
                        print(e)
                        print(message, "Failed to send pushover message")
                else:
                    print("{}: No appointments during the next {} days.".format(city, DAYS_OUT))
            else:
                print("{}: No appointments during the next {} days.".format(city, DAYS_OUT))
            time.sleep(1)
        time.sleep(TIME_WAIT)
except KeyboardInterrupt:
    sys.exit(0)
