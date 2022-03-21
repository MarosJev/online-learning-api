#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 20:25:40 2022

@author: Maros Jevocin
"""
from os.path import exists
from flask import Flask, request, url_for, jsonify

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import preprocessing as prep
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline, FeatureUnion, make_pipeline
import dill


app = Flask(__name__)



# method for preparing the model from the assignment GitHub repository
def column_selector(column_name):
    
    return prep.FunctionTransformer(
        lambda X: X[column_name], validate=False)




@app.route('/sample', methods=['POST'])
def sample():
    
    payload = request.get_json()
    df_json = pd.DataFrame.from_dict(payload)
    
    # Dropping redundant column with indexes
    if ('' in list(df_json.keys())):
        df_json = df_json.drop(columns=[''])
    
    
    model_file_name = 'naive_bayes_classifier.pkl'
    
    if (exists(model_file_name)):
        # if model already exists
        model = dill.load(open('naive_bayes_classifier.pkl', 'rb'))
        # making a prediction
        prediction = model.predict(df_json.loc[:,['CompanyId', 'BankEntryText', 'BankEntryAmount']])
        df_json['AccountNumberPredicted'] = prediction
        
        model_score = model.score(df_json, df_json.AccountNumber.values.astype(int))
        
        print('-------')
        print('Predictions on samples:\n', df_json.loc[:,['CompanyId', 'BankEntryText', 'BankEntryAmount', 'AccountNumber','AccountNumberPredicted']])
        print('-------')
        print('Model score:', model_score)
        print('-------')
    else:
        # if model does not exist yet, we create one
        
        print('Creating the model for the first time.')
        # adding a blank prediction column for the first sample entry
        df_json['AccountNumberPredicted'] = ['' for i in range(df_json.shape[0])]

        # --- Model from https://github.com/e-conomic/hiring-assignments/tree/master/machinelearningteam/online-learning-api
        
        # let's build classifiers
        # bag of words for the text feature
        vectorizer = CountVectorizer(max_features=10000)
        # we need a few OneHotEncoders - but I don't like the interface for that and this has the same effect
        # bag of words when all texts are max of one word => one-hot encoding
        amount_encoder = CountVectorizer(max_features=50)  
        companyId_encoder = CountVectorizer(max_features=500)  
        # combine before doing the regression - feature union requires all features to have the same interface,
        # so to make this work we need to project onto a single column first for each
        all_features = FeatureUnion(
            [
                ['company', make_pipeline(column_selector('CompanyId'), companyId_encoder)],
                ['text', make_pipeline(column_selector('BankEntryText'), vectorizer)], 
                ['amount', make_pipeline(column_selector('BankEntryAmount'),amount_encoder )],
            ])
        classifier = MultinomialNB()
        # pipeline the whole thing
        model = Pipeline([('features', all_features), ('nb', classifier)])
        
        # --- End of model definition 
        
        
    # storing samples
    if (not exists('samples.csv')):
        df_json.to_csv('samples.csv', mode='w', index=False, header=True)
    else:
        df_json.to_csv('samples.csv', mode='a', index=False, header=False)
    
    df_samples = pd.read_csv('samples.csv')
    #print(df_samples)
    
    # now train the classifier on updated samples csv file
    model.fit(df_samples, df_samples.AccountNumber)
    if(exists(model_file_name)):
        print('model score after new training: ', model.score(df_json, df_json.AccountNumber.values.astype(int)))
    # dump model object
    dill.dump(model, open(model_file_name, 'wb'))
    
    return(jsonify({'message' : 'The sample has been accepted and model has been retrained.'}))
    
    
    
    
@app.route('/predict', methods=['POST'])
def predict():
    
    payload = request.get_json()
    df_json = pd.DataFrame.from_dict(payload)
    #print(df_json)
    
    # Dropping redundant column with indexes
    if ('' in list(df_json.keys())):
        df_json = df_json.drop(columns=[''])
        
    model_file_name = 'naive_bayes_classifier.pkl'
    
    # return a message if the model doesn't exist yet
    if (not exists(model_file_name)):
        return(jsonify({'message' : 'Unable to provide a prediction. The model doesn\'t exist yet.'}))
        
    else:
        # if json includes more or less than one sample
        if (df_json.shape[0] != 1):
            return(jsonify({'message' : 'The /predict method only accepts a single sample record.'}))
        
        # loading the model
        model = dill.load(open('naive_bayes_classifier.pkl', 'rb'))
        # making a prediction
        prediction = model.predict(df_json.loc[:,['CompanyId', 'BankEntryText', 'BankEntryAmount']])
    
    return(jsonify({'AccountNumber' : str(prediction[0])}))
    
    
    
    
    
@app.route('/getStatus', methods=['GET'])
def getStatus():
    
    return(jsonify({'message' : 'Success!'}))
    
    
    
    
    
@app.errorhandler(500)
def page_not_found(error):
    return str(error)

with app.test_request_context():
    print(url_for('sample'))
    print(url_for('predict'))