#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 17:51:05 2022

@author: marosj
"""

import requests
import pandas as pd
from os.path import exists
import traceback


api_url = "http://127.0.0.1:5000"

#response = requests.get(api_url)
#response.json()

def print_context():
    print(">>>> Here is a list of available actions to execute, enter corresponding number to start:")
    print("-----")
    print("1 : to provide a path to sample .csv file for the model training.")
    print("2 : to provide CompanyId, BankEntryText and BankEntryAmount to retrieve AccountNumber suggestion by our learning API.")
    print("3 : to retrieve the current model score.")
    print("0 : to exit.")
    print("-----")

def main():
    print("Welcome to the online learning api client!")
    
    
    while(True):
            
        try:
                
            print_context()
            input_option = input()
            
            # to exit client
            if(input_option == "0"):
                break
                
            # to send a sample to the Rest API for the model training
            elif(input_option == "1"):
                print(">>>> Enter path to the .csv sample file.")
                input_csv_path = input()
                
                print("------\n")
                print(">>>> Result:")
                
                # only send a sample if the .csv file exists
                if (exists(input_csv_path)):
                    sample = pd.read_csv(input_csv_path).to_dict()
                    
                    response = requests.post(api_url + '/sample', json=sample)
                    print(response.json()['message'])
                    
                else:
                    print("The file with such path does not exist.")
                print("------\n")
            
            
            
            
            # to send a sample to the Rest API for a prediction
            elif(input_option == "2"):
                print(">>>> Enter CompanyId, Bank Entry Text, Bank Entry Amount. (separate values with comma)")
                input_predict_sample = input()
                
                print("------\n")
                print(">>>> Result:")
                
                input_list = input_predict_sample.split(',')
                map(str.strip, input_list)
                
                predict_sample = [{
                        'CompanyId' : input_list[0],
                        'BankEntryText' : input_list[1],
                        'BankEntryAmount' : input_list[2]
                        }]
                response = requests.post(api_url + '/predict', json=predict_sample)
                print(str(response.json()))
                
                print("------\n")
                
            elif(input_option == "3"):
                continue
            else:
                print("Invalid option.\n")
                print_context()
        
        except:
            print(traceback.print_exc())
            print("-----\n")
        

if __name__ == "__main__":
    main()
