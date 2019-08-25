#!/usr/bin/env python3

from bluepy import btle
from struct import unpack
import boto3
from time import sleep

mac = "d8:a9:8B:75:43:2d"

while True:

    try:
        dev = btle.Peripheral(mac)
        readings = dev.readCharacteristic(40)
    except Exception as e:
        print("Error reading BTLE: {}".format(e))
        continue
    finally:
        dev.disconnect()

    temperature_c, humidity = unpack("<HH",readings[0:4])
    temperature_f = 9.0/5.0 * temperature_c / 100 + 32

    print("temperature is {}".format(temperature_f))

    try:
        client = boto3.client('cloudwatch')
        response = client.put_metric_data(
            Namespace='brewing',
            MetricData=[
                {
                    'MetricName': 'keezer',
                    'Dimensions': [
                        {
                            'Name': 'temperature_f',
                            'Value': 'degrees'
                        },
                    ],
                    'Value': temperature_f,
                    'Unit': 'Count'
                },
            ]
        )
    except Exception as e:
        print("Error submitting metric: {}".format(e))
        continue

    sleep(30)
