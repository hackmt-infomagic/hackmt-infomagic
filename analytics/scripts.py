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
    session['start'] = datetime.strptime(session['start'], '%Y/%m/%d %H:%M:%d')
    session['end']   = datetime.strptime(session['end'],   '%Y/%m/%d %H:%M:%d')

def convert_start_delta(user_data):
  '''Convert raw timestamps to a datetime and timedelta'''
  for session in user_data['sessions']:
    session['start'] = datetime.strptime(session['start'], '%Y/%m/%d %H:%M:%S')
    session['end']   = datetime.strptime(session['end'], '%Y/%m/%d %H:%M:%S') - session['start']

def to_start_delta(user_data):
  '''Convert from two datetime objects to a datetime and timedelta'''
  for session in user_data['sessions']:
    session['end']   = session['end'] - session['start']


def subject_totals(user_data):
  '''Reurn the total time spent studying each subject for the given user.'''

  # Initialize a dict of subject -> total
  totals = {subject : timedelta() for subject in user_data['subjects']}
  
  for session in user_data['sessions']:
    totals[session['subject']] += session['end']

  return totals


def user_total(user_data):
  '''Return the total number of hours a user has studied'''

  total = timedelta()
  for session in user_data['session']:
    total += session.end

  return total


def calc_global_probabilities(user_data):
    '''Calculate global probabilities'''
    probabilities = numpy.zeros(len(user_data['subjects']))
    total = 0.0
    convert_start_delta(user_data)
    for session in user_data['sessions']:
        probabilities[user_data['subjects'].index(session['subject'])] += session['end'].total_seconds()
        print(session['end'].total_seconds())
        total += session['end'].total_seconds()
    probabilities /= total
    return(probabilities)


def cumulative(user_data, num_bins):
  '''
  '''
  global_start = user_data['sessions'][0]['start']
  global_end   = user_data['sessions'][-1]['start']

  # The duration of a single bin
  step_size = (global_end - global_start) / num_bins

  # The datetime marking the end of the current bin
  curr_bin_end = global_start + step_size

  # The total for the current bin
  curr_bin_total = timedelta()

  # The list of bin totals
  bin_data = []

  # Assumes sessions are in chronological order
  for session in user_data['sessions']:
    # Should really be checking end times
    if session['start'] < curr_bin_end:
      curr_bin_total += session['end']
    else:
      bin_data.append(curr_bin_total)
      curr_bin_total = session['end']
      curr_bin_end += step_size

  # Ensure that len(bin_data) == num_bins
  for _ in range(num_bins - len(bin_data)):
    bin_data.append(timedelta())

  return bin_data


