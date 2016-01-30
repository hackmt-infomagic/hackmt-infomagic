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
  for session in user_data['sessions']:
    session['start'] = datetime.strptime(session['start'], '%Y/%m/%d %H:%M:%S')
    session['end']   = datetime.strptime(session['end'],   '%Y/%m/%d %H:%M:%S')

def convert_start_delta(user_data):
  '''Convert raw timestamps to a datetime and timedelta'''
  for session in user_data['sessions']:
    session.['start'] = datetime.strptime(session['start'], '%Y/%m/%d %H:%M:%S')
    session.['end']   = datetime.strptime(session['end'], '%Y/%m/%d %H:%M:%S')- session['start']

def to_start_delta(user_data):
  '''Convert from two datetime objects to a datetime and timedelta'''
  for session in user_data['sessions']:
    session['end']   = session['end'] - session['start']

def to_raw_timestamps(user_data):
    '''Convert two datetime objects to raw timestamps'''
    for session in user_data['sessions']:
        session['start'] = session['start'].strftime('%Y/%m/%d %H:%M:%S')
        session['end']   = session['end'].strftime('%Y/%m/%d %H:%M:%S')

def to_start_end(user_data):
    '''Convert datetime and timedelta to two datetime objects'''
    for session in user_data['sessions']:
        session['end']   = session['start'] + session['end']
                    
def subject_totals(user_data):
  '''Reurn the total time spent studying each subject for the given user.'''

  # Initialize a dict of subject -> total
  totals = {subject : timedelta() for subject in user_data['subjects']}
  
  for session in user_data.sessions:
    totals[session['subject']] += session['end']

  return totals


def user_total(user_data):
  '''Return the total number of hours a user has studied'''

  total = timedelta()
  for session in user_data.session:
    total += session.end

  return total

def calc_global_probabilities(user_data):
    '''Calculate global probabilities of events given a list of sessions - including gaps'''
    subjects = user_data['subjects']
    probabilities = numpy.zeros(len(user_data['subjects'])+1)
    convert_start_delta(user_data)
    lastend = user_data['sessions'][0]['start']
    total = 0.0
    for session in user_data['sessions']:
        session_time = session['end']
        gap_time = session['start'] - lastend
        probabilities[user_data['subjects'].index(session['subject'])] += session_time.total_seconds()
        probabilities[len(probabilities)-1] += gap_time.total_seconds()
        total += session_time.total_seconds() + gap_time.total_seconds()
        lastend += session_time + gap_time
    probabilities /= total
    to_start_end(user_data)
    to_raw_timestamps(user_data)
    return(probabilities)
