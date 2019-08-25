#!/usr/bin/env python3

from bluepy import btle
from struct import unpack
import boto3
from time import sleep
import logging
logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

mac = "d8:a9:8B:75:43:2d"

while True:

    try:
        dev = btle.Peripheral(mac)
        readings = dev.readCharacteristic(40)
    except Exception as e:
        logging.error("Error reading BTLE: {}".format(e))
        continue
    finally:
        dev.disconnect()

    logging.debug("raw data: {}".format(readings[0:4]))
    [temperature_c, humidity] = [n / 100 for n in unpack("<HH",readings[0:4])]
    temperature_f = 9.0/5.0 * temperature_c + 32
    logging.info("converted data: temperature_f[{}], temperature_c[{}], humidity[{}]".format(temperature_f, temperature_c, humidity))

    logging.info("temperature_f is {}".format(temperature_f))

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
        logging.error("Error submitting metric: {}".format(e))
        continue

    sleep(30)
