import logging
import boto3
from botocore.exceptions import ClientError

from threading import Thread

class ShopDealSNS:
    def send_SMS_message(self, mobile, my_message):
        try:
            sns_client = boto3.client('sns')
            print('\ndelivering the message {} to {}...\n'.format(my_message, mobile))
            # use the method publish() of the SNS Client API to deliver a message to a specified phone
            sns_client.publish(PhoneNumber=mobile, Message=my_message)
            
        except ClientError as e:
            logging.error(e)
            return False
        return True