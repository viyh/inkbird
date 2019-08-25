#!/usr/bin/env python3

from bluepy import btle
from struct import unpack
import boto3

mac = "FILL_THIS_IN"

dev = btle.Peripheral(mac)
readings = dev.readCharacteristic(40)

temperature_c, humidity = unpack("<HH",readings[0:4])
temperature_f = 9.0/5.0 * temperature_c / 100 + 32

print("temperature is {}".format(temperature_f))

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
