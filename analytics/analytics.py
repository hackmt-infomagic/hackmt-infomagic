#!/usr/bin/env python3

from datetime import datetime, timedelta
from pymongo import MongoClient
from math import ceil

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
    session['start'] = datetime.strptime(session['start'], '%Y/%m/%d %H:%M:%S')
    session['end']   = datetime.strptime(session['end'], '%Y/%m/%d %H:%M:%S') - session['start']

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


def split_session(session, offset):
  '''

  offset : a duration specifying how far into the session to make the split
  '''

  # The datetime of the split
  middle = session['start'] + offset

  one = {'subject': session['subject'], 'start': session['start'],
         'end': middle - session['start'], 'tags': session['tags']}

  two = {'subject': session['subject'], 'start': middle,
         'end': (session['start'] + session['end']) - middle, 'tags': session['tags']}

  return (one, two)


def bin_data(user_data, bin_duration):
  '''
  '''
  global_start = user_data['sessions'][0]['start']
  global_end   = user_data['sessions'][-1]['start'] + user_data['sessions'][-1]['end']

  num_bins = int(ceil((global_end - global_start) / bin_duration))

  # End datetime of the current bin
  end_curr_bin = global_start + bin_duration

  curr_bin_data = []

  bin_data = []

  # Number of sessions in user_data['sessions']
  num_sessions = len(user_data['sessions'])

  # Index of the next session in user_data['sessions']
  next_ind = 0

  # Holds the remainder if splitting occurs 
  remainder = []

  # Fill each bin
  for i in range(num_bins):
    # Check if the remainder overflows
    if len(remainder) > 0:
      if (remainder[0]['start'] + remainder[0]['end']) > end_curr_bin:
        one, two = split_session(remainder[0], end_curr_bin - remainder[0]['start'])
        bin_data.append([one])
        remainder = [ two ]
        end_curr_bin += bin_duration
        continue
      else:
        curr_bin_data.append(remainder[0])
        remainder = []

    # Add sessions to this bin until we run out or go over
    while (next_ind < num_sessions and
           user_data['sessions'][next_ind]['start'] < end_curr_bin):
      # Get reference to next session
      session = user_data['sessions'][next_ind]

      # End of the next session
      session_end = session['start'] + session['end']

      # Check for boundary crossing
      if session_end <= end_curr_bin:
        curr_bin_data.append(session)
      else:
        one, two = split_session(session, end_curr_bin - session['start'])
        curr_bin_data.append(one)
        remainder = [ two ]

      # Increment index of next session
      next_ind += 1
    #End while --------------------------

    bin_data.append(curr_bin_data)
    end_curr_bin += bin_duration
    curr_bin_data = []

  return bin_data


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


