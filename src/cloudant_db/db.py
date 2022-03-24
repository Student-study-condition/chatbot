import os
from typing import Dict
from urllib import response
from dotenv import load_dotenv
import json
import pandas as pd
from ibmcloudant.cloudant_v1 import CloudantV1, Document
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pydantic import Json

load_dotenv()

class UserDatabase:
        
    #get IAM token for session    
    def __init__(self):
        self.authenticator = IAMAuthenticator(os.getenv('CLOUDANT_APIKEY'))
        self.service = CloudantV1(authenticator=self.authenticator)
        self.service.set_service_url(os.getenv('CLOUDANT_URL'))

        self.db_name = 'user-account'

    def get_database(self):
        response = self.service.get_all_dbs().get_result()
        return(response)

    def get_database_information(self):
        response = self.service.get_database_information(db='user-account').get_result()
        return(response)

    def add_user(self, id: str, username: str, firstname: str, lastname: str):
        new_user = Document(
            id=id,
            username=username,
            firstname=firstname,
            lastname=lastname)
        try:
            response = self.service.new_instance().post_document(db=self.db_name, document=new_user).get_result()
            return response
        except:
            return 'user is exist'
        

    def remove_user(self, id: str):
        user_rev = self.get_user(id)['_rev']
        response = self.service.delete_document(
              db=self.db_name,
              doc_id=id,
              rev=user_rev).get_result()

        return response

    def get_user(self, id: str):
        try:
            response = self.service.get_document(
          db=self.db_name,
          doc_id=id).get_result()

            return response
        except: 
            return 'error'

    def register_study_device(self, id: str, registerDevice: dict=None):
        old_data = self.get_user(id)
        print(old_data.keys())
        user_rev = old_data['_rev']

        #handle new data
        try:
            registerDevices = old_data.registerDevices
        except:
            registerDevices = []

        if registerDevice != None:
            registerDevices.append(registerDevice)
        
        edit_doc = Document(
          rev=user_rev,

          username=old_data['username'],
          firstname=old_data['firstname'],
          lastname=old_data['lastname'],
          registerDevices=registerDevices        
        )
        response = self.service.put_document(
          db='user-account',
          doc_id=id,
          document=edit_doc
        ).get_result()

        return response

    def find(self, firstname: str):
        selector = {
            "index.name": firstname
        }

        response = self.service.post_find(
          db='iot',
          selector=selector,
          limit=10
        ).get_result()

        return response['docs']

class IOTdatabase:
        
    #get IAM token for session    
    def __init__(self):
        self.authenticator = IAMAuthenticator(os.getenv('CLOUDANT_APIKEY'))
        self.service = CloudantV1(authenticator=self.authenticator)
        self.service.set_service_url(os.getenv('CLOUDANT_URL'))

        self.db_name = 'user-account'

    def get_device_hist(self, iot_device_name: str):
        selector = {
            "index.name": iot_device_name
        }

        response = self.service.post_find(
          db='iot',
          selector=selector
        ).get_result()

        return response['docs']

    def get_stat(self, iot_device_name: str):
        selector = {
            "index.name": iot_device_name
        }

        response = self.service.post_find(
          db='iot',
          selector=selector
        ).get_result()

        # print(pd.DataFrame(response['docs']).head(20))

        payload = []
        for res in response['docs']:
            payload.append(res['d'])

        df = pd.DataFrame(payload)
        
        temp = df['temperature']
        humidity = df['humidity']
        illuminance = df['illuminance']
        sound = df['sound']
        
        prefered_condition = {
            "temperature": temp.median(),
            "temp_std": temp.std(),
            "humidity": humidity.median(),
            "humi_std": humidity.std(),  
            "illuminance": illuminance.median(),
            "illu_std": illuminance.std(),  
            "sound": sound.median(),
            "sound_std": sound.std(), 
            "data_size": df['sound'].count() + 1   
        }

        return prefered_condition

    def check_device_exist(self, device_id):
        try:
            response = self.service.get_document(
            db='iot-device',
            doc_id=device_id).get_result()

            return True

        except:
            return False
        


if __name__ == "__main__":
    database = UserDatabase()
    iotdb = IOTdatabase()



    # print(iotdb.check_device_exist('4C11AE917C14'))
    # print(iotdb.check_device_exist('4C11AE917C14e'))
    # print(iotdb.get_device_hist('dfafadsfaf'))

    print("dataA = ", iotdb.get_stat('DEVICE_ID'))
    # print("\n")
    print("dataB = ",iotdb.get_stat('4C11AE917C14'))
    print("dataC = ",iotdb.get_stat('NOISY-LOC'))
    print("dataD = ",iotdb.get_stat('VERY-BRIGHT'))
    
    # print("all_db = ", database.get_database())
    # print("db_info = ", database.get_database_information())
    # print("\n")

    # print("add user = ", database.add_user('123456', 'johnnycneas', 'john', 'cnea'))
    # print(database.get_user('123456'))
    # print(database.get_user('12345677'))
    # print("rm", database.remove_user('123456'))
    # # print(database.register_study_device('123456'))
    # print(database.find('4C11AE917C14'))

    
