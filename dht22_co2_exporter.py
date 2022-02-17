#!/usr/bin/env python3

# Prometheus exporter for DHT22 running on raspberrypi
# Usage: ./dht22_exporter -g <gpio_pin_number> -i <poll_time_in_seconds> [-a <exposed_address> -p <exposed_port>]
# Ex: ./dht22_exporter -g 4 -i 2

import time
import argparse

from prometheus_client import Gauge, start_http_server

import Adafruit_DHT
import mh_z19

# Create a metric to track time spent and requests made.
dht22_temperature_celsius = Gauge(
    'dht22_temperature_celsius', 'Temperature in celsius provided by dht sensor')
dht22_temperature_fahrenheit = Gauge(
    'dht22_temperature_fahrenheit', 'Temperature in fahrenheit provided by dht sensor')
dht22_humidity = Gauge(
    'dht22_humidity', 'Humidity in percents provided by dht sensor')

mh_z19_co2 = Gauge(
    'mh_z19_co2', 'CO2 in ppm provided by MH_Z19 sensor')
mh_z19_raw_temperature_celsius = Gauge(
    'mh_z19_raw_temperature_celsius', 'Raw (with offset) Temperature in celsius provided by MH_Z19 sensor')
mh_z19_unnamed = Gauge(
    'mh_z19_unnamed', 'Unnamed value provided by MH_Z19 sensor')

SENSOR = Adafruit_DHT.DHT22


def read_sensors(pin):
    humidity, dht22_temperature = Adafruit_DHT.read_retry(SENSOR, pin)
    mh_z19_data = mh_z19.read_all()
    co2 = mh_z19_data['co2']
    mh_z19_raw_temperature = mh_z19_data['TT']
    unnamed_value = mh_z19_data['UhUl']

    if humidity is None or dht22_temperature is None:
        return

    if humidity > 200 or dht22_temperature > 200:
        return

    dht22_humidity.set('{0:0.1f}'.format(humidity))
    dht22_temperature_fahrenheit.set(
        '{0:0.1f}'.format(9.0/5.0 * dht22_temperature + 32))
    dht22_temperature_celsius.set(
        '{0:0.1f}'.format(dht22_temperature))

    mh_z19_co2.set(f'{co2}')
    mh_z19_raw_temperature_celsius.set(f'{mh_z19_raw_temperature}')
    mh_z19_unnamed.set(f'{unnamed_value}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gpio", dest="gpio", type=int,
                        required=True, help="GPIO pin number on which the sensor is plugged in")
    parser.add_argument("-a", "--address", dest="addr", type=str, default=None,
                        required=False, help="Address that will be exposed")
    parser.add_argument("-i", "--interval", dest="interval", type=int,
                        required=True, help="Interval sampling time, in seconds")
    parser.add_argument("-p", "--port", dest="port", type=int, default=8001,
                        required=False, help="Port that will be exposed")

    args = parser.parse_args()

    if args.addr is not None:
        start_http_server(args.port, args.addr)
    else:
        start_http_server(args.port)

    while True:
        read_sensors(pin=args.gpio)
        time.sleep(args.interval)


main()
