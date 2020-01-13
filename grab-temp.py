#!/usr/bin/env python3

# Get values from Inkbird IBS-TH1 and submit to Cloudwatch

from time import sleep
from bluepy import btle
import boto3
import logging

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

mac = "d8:a9:8B:75:43:2d"
read_interval = 30

def float_value(nums):
    return float((nums[1]<<8)|nums[0]) / 100

def c_to_f(temperature_c):
    return 9.0/5.0 * temperature_c + 32

def get_readings():
    try:
        dev = btle.Peripheral(mac, addrType=btle.ADDR_TYPE_PUBLIC)
        readings = dev.readCharacteristic(0x28)
        return readings
    except Exception as e:
        logging.error("Error reading BTLE: {}".format(e))
        return False

def submit_metric(namespace, metric_name, dimensions, value, unit='Count'):
    try:
        client = boto3.client('cloudwatch')
        response = client.put_metric_data(
            Namespace=namespace,
            MetricData=[
                {
                    'MetricName': metric_name,
                    'Dimensions': dimensions,
                    'Value': value,
                    'Unit': unit
                },
            ]
        )
    except Exception as e:
        logging.error("Error submitting metric: {}".format(e))
        pass

while True:
    sleep(read_interval)
    readings = get_readings()
    if not readings:
        continue

    logging.debug("raw data: {}".format(readings))

    # little endian, first two bytes are temp_c, second two bytes are humidity
    temperature_c = float_value(readings[0:2])
    humidity = float_value(readings[2:4])
    temperature_f = c_to_f(temperature_c)

    logging.info("converted data: temperature_f[{:0.2f}], temperature_c[{:0.2f}], humidity[{:0.2f}]".format(temperature_f, temperature_c, humidity))

    if temperature_f > 100:
        continue
    submit_metric('brewing', 'temperature_f', [{'Name': 'Location', 'Value': 'keezer'}], temperature_f)
    submit_metric('brewing', 'humidity', [{'Name': 'Location', 'Value': 'keezer'}], humidity)
