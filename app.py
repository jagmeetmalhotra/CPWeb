from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify
import json
import os.path
import os
from werkzeug.utils import secure_filename
import pandas as pd
import fasttext
import numpy as np
import re
import string
import pickle


app= Flask(__name__)
app.secret_key = 'h432hi5ohi3h5i5hi3o2hi'
model = pickle.load(open('logreg_model_deploy.sav','rb'))

encoder_mapping = {0: 'GRP_0', 1: 'GRP_12', 2: 'GRP_13', 3: 'GRP_14', 4: 'GRP_19', 5: 'GRP_2', 6: 'GRP_24', 7: 'GRP_25', 8: 'GRP_29', 9: 'GRP_3', 10: 'GRP_33', 11: 'GRP_4', 12: 'GRP_8', 13: 'GRP_MANUAL'}

def clean_text_before_lang_detect(text  ):
    #remove _x000D_
    text = re.sub(r'_x000D_', '',text)
    #remove tabs
    text = re.sub(r'\t', '',text)
    #remove puntuations
    text = text.translate(str.maketrans('','',string.punctuation))
    # Remove new line characters 
    text = re.sub(r'\n',' ',text)
    #Remove leading & trailing Spaces
    text = re.sub(r"^\s+|\s+$", "", text)
    # Remove numbers and special chaacters
    text = re.sub(r'\d+','' ,text)
    text = re.sub(r'\/\/',' ', text)
    text = re.sub(r'\\',' ', text)
    text = re.sub(r'\(',' ', text)
    text = re.sub(r'\)',' ', text)
    text = re.sub(r':' ,' ', text)
    text = re.sub(r'-' ,' ', text)
    text = re.sub(r'\/',' ', text)
    text = re.sub(r'\.',' ', text)
    text = re.sub(r'\,',' ', text)
    #Remove email 
    text = re.sub(r'\S*@\S*\s?', '', text)
    # Remove hyperlinks
    text = re.sub(r'https?:\/\/.*\/\w*', '', text)
    # Remove hashtag while keeping hashtag text
    text = re.sub(r'#','', text)
    #remove '_'
    text = re.sub(r'_',' ',text)
    #remove additional spaces 
    text = re.sub(' +', ' ', text)
    text=text.lower()
    text = text.strip()
    return text


def clean_data_domainContext(text  ):
    text = re.sub(r"received from:",'',text)
    text = re.sub(r"received:",'',text)
    text = re.sub(r"hi",' ',text)
    text = re.sub(r"this message was sent from an unmonitored email address",'',text)
    text = re.sub(r"email:",' ',text)
    text = re.sub(r"email address:",'',text)
    text = re.sub(r"from:",' ',text)
    text = re.sub(r"sddubject:",'',text)
    text = re.sub(r"please do not reply to this message",' ',text)
    text = re.sub(r"select the following link to view the disclaimer in an alternate language",' ',text)
    text = re.sub(r"description problem",'',text)
    text = re.sub(r"steps taken far",' ',text)
    text = re.sub(r"please do the needful",'',text)
    text = re.sub(r"customer job title",' ',text)
    text = re.sub(r"sales engineer contact",'',text)
    text = re.sub(r"please note that",' ',text)
    text = re.sub(r"please find below",'',text)
    text = re.sub(r"hello",'',text)
    text = re.sub(r"date and time",' ',text)
    text = re.sub(r"kindly refer mail:",'',text)
    text = re.sub(r"name:",' ',text)
    text = re.sub(r"language:",'',text)
    text = re.sub(r"customer number:",' ',text)
    text = re.sub(r"telephone:",'',text)
    text = re.sub(r"summary:",' ',text)
    text = re.sub(r"sincerely",'',text)
    text = re.sub(r"company inc",' ',text)
    text = re.sub(r"hallo",'',text)
    text = re.sub(r"hi it team",' ',text)
    text = re.sub(r"hi team",'',text)
    text = re.sub(r" hi ",'',text)
    text = re.sub(r"best",' ',text)
    text = re.sub(r" na ",' ',text)
    text = re.sub(r" yes ",' ',text)
    text = re.sub(r" kind ",'',text)
    text = re.sub(r" regards ",' ',text)
    text = re.sub(r" good morning ",'',text)
    text = re.sub(r" please ",'',text)
    text = re.sub(r"monitoring_tool@company.com",'MonitoringTool',text)
    #Remove email 
    text = re.sub(r'\S*@\S*\s?', '', text)
    text = text.translate(str.maketrans('','',string.punctuation))
    text = re.sub(' +', ' ', text)
    text = text.strip()
    return text

@app.route('/')
def home():
    return render_template('home.html', codes=session.keys())

@app.route('/your-ticket', methods=['GET','POST'])
def your_ticket():
    if request.method == 'POST':
        sd =  request.form['sd']
        desc = request.form['desc']
        en_desc = sd + " " + desc
        en_desc = re.sub(r'\n','',en_desc)
        en_desc = clean_text_before_lang_detect(en_desc)
        en_desc = clean_data_domainContext(en_desc)
        result = model.predict([en_desc])
        print("Result :"+ str(result));
        flash("Your ticket has been assinged to Assignment Group : " + encoder_mapping[result[0]] )
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))



@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


