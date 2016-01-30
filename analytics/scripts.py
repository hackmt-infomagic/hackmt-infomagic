#!/usr/bin/env python3

from datetime import datetime, timedelta

from pymongo import MongoClient

def get_document(user_id):
    client = MongoClient('mongodb://hackmt-infomagic:hackmt1!@ds051655.mongolab.com:51655/hackmt-infomagic')
    db = client['hackmt-infomagic']
    collection = db['Users']
    # silent error
    match = collection.find({'user_id':user_id})[0]
    return (match)

def convert_start_end(user_data):
  '''Convert raw timestamps to datetime objects'''
  for session in user_data.sessions:
    session.start = datetime.strptime(session.start, '%Y/%m/%d %H/%M/%d')
    session.end   = datetime.strptime(session.end,   '%Y/%m/%d %H/%M/%d')

def convert_start_delta(user_data):
  '''Convert raw timestamps to a datetime and timedelta'''
  for session in user_data.sessions:
    session.start = datetime.strptime(session.start, '%Y/%m/%d %H/%M/%d')
    session.end   = session.end - session.start

def to_start_delta(user_data):
  '''Convert from two datetime objects to a datetime and timedelta'''
  for session in user_data.session:
    session.end   = session.end - session.start
