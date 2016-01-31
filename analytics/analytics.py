#!/usr/bin/env python3

from datetime import datetime, timedelta
from pymongo import MongoClient
from math import ceil

def get_db_connection():
    client = MongoClient('mongodb://hackmt-infomagic:hackmt1!@ds051655.mongolab.com:51655/hackmt-infomagic')
    db = client['hackmt-infomagic']
    return db


def get_document(user_id):
    client = MongoClient('mongodb://hackmt-infomagic:hackmt1!@ds051655.mongolab.com:51655/hackmt-infomagic')
    db = client['hackmt-infomagic']
    collection = db['Users']
    # silent error
    match = collection.find({'user_id':user_id})[0]
    return (match)


def push_stats(db, user_id,key,data):
    db['Users'].update_one(
    {'user_id': user_id},
    {'$set' : {'stats.{:s}'.format(key) : data}}
    )


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


def subject_totals_hours(user_data):
  totals = subject_totals(user_data)
  for key in totals.keys():
    totals[key] = totals[key].total_seconds() / 3600

  return totals


def total(user_data):
  '''Return the total number of hours a user has studied'''

  total = timedelta()
  for session in user_data['sessions']:
    total += session['end']

  return total


def calc_global_probabilities(user_data):
    '''Calculate global probabilities of events given a list of sessions - including gaps'''
    ## Setup timestamps as datetime-timedelta
    convert_start_delta(user_data)

    subjects = user_data['subjects'] + ['Not Tracked']
    n = len(subjects)
    state_probabilities = numpy.zeros(n)
    ## Using this to avoid divide-by-zero, for now...
    transition_probabilities = numpy.zeros((n,n))+0.00000001
    lastend = user_data['sessions'][0]['start']
    total = 0.0
    gaps = []


    ## Calculate overall state probabilities and gap lengths
    for session in user_data['sessions']:
        session_time = session['end']
        gap_time = session['start'] - lastend
        state_probabilities[user_data['subjects'].index(session['subject'])] += session_time.total_seconds()
        state_probabilities[n-1] += gap_time.total_seconds()
        total += session_time.total_seconds() + gap_time.total_seconds()
        lastend += session_time + gap_time
        gaps.append(gap_time.total_seconds())
    state_probabilities /= total
    gaps = numpy.array(gaps[1:])

    ## Calculate kernel density estimate of user gaps
    kde = KernelDensity(kernel='gaussian',bandwidth=300).fit(numpy.array(gaps).reshape(-1,1))
    x_plot = numpy.linspace(0,max(gaps),1000)[:,numpy.newaxis]
    dens = numpy.exp(kde.score_samples(x_plot))
    ## Could plot this with matplotlib
    ## fig,ax = plot.subplots(1,1,sharex=True,sharey=True)
    ## ax.plot(x_plot[:,0],dens,'-',label="gap density")
    ## ax.plot(x_plot[dens.tolist().index(max(dens))],max(dens),'or')

    ## Calculate bottom 50%
    total = 0.0
    for x in range(len(dens)):
        total += dens[x]
        if total/sum(dens) > 0.75:
            break
    cutoff = numpy.asscalar(x_plot[x])
    ## ax.plot(x_plot[x],dens[x],'or')
    ## plot.show()
    
    ## Set long gaps to zero, since they are not part of the bottom half (connected events)
    gaps[gaps > cutoff] = 0.0
    
    ## Calculate transition probabilities using non-zero gaps
    for x in range(len(sessions)-1):
        if gaps[x] > 0.0 and sessions[x]['subject'] != sessions[x+1]['subject']:
            transition_probabilities[subjects.index(sessions[x]['subject']),subjects.index(sessions[x+1]['subject'])] += 1.0
        else:
            transition_probabilities[subjects.index(sessions[x]['subject']),len(subjects)-1] += 1.0
            transition_probabilities[len(subjects)-1,subjects.index(sessions[x+1]['subject'])] += 1.0

    ## Normalization
    t_from = transition_probabilities / transition_probabilities.sum(axis=1)[:,numpy.newaxis]
    t_to = transition_probabilities / transition_probabilities.sum(axis=0)
    t_joint = transition_probabilities / transition_probabilities.sum()
    
    ## Cutoff for relevance
    t_from[t_from<0.00000001] = 0.0
    t_to[t_to<0.00000001] = 0.0
    
    ## Convert timestamps back to standard storage
    to_start_end(user_data)
    to_raw_timestamps(user_data)

    return({'P':state_probabilities,
            'from':t_from,
            'to':t_to,
            'joint':t_joint})


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


def datetime_to_string(dt):
  return dt.strftime('%Y/%m/%d %H:%M:%S')


def global_start(user_data):
  return user_data['sessions'][0]['start']


def global_start_string(user_data):
  return datetime_to_string(global_start(user_data))


def global_end(user_data):
  return user_data['sessions'][-1]['start'] + user_data['sessions'][-1]['end']


def global_end_string(user_data):
  return datetime_to_string(global_end(user_data))


def cumulative(user_data, num_bins=100):
  '''
  '''

  bin_duration = (global_end(user_data) - global_start(user_data)) / num_bins

  bdata = bin_data(user_data, bin_duration)

  sums = []
  for b in bdata:
    curr_sum = timedelta()
    for session in b:
      curr_sum += session['end']
    sums.append(curr_sum)

  cums = [sums[0]]
  for j in range(1, len(sums)):
    cums.append(sums[j] + cums[j-1])

  return cums

def cumulative_hours(user_data):
  cums = cumulative(user_data)
  return [cum.total_seconds() / 3600 for cum in cums]


def subject_cumulatives(user_data, num_bins=100):

  # Dictionary of lists
  subject_cums = {subject : [] for subject in user_data['subjects']}

  bin_duration = (global_end(user_data) - global_start(user_data)) / num_bins

  bdata = bin_data(user_data, bin_duration)

  for b in bdata:
    curr_subject_cums = {subject : timedelta() for subject in user_data['subjects']}

    # Get per-subject sums for this bin
    for session in b:
      curr_subject_cums[session['subject']] += session['end']
 
    for subject in user_data['subjects']:
      subject_cums[subject].append(curr_subject_cums[subject])

  # make cumulative
  for key in subject_cums.keys():
    for i in range(1, len(subject_cums[key])):
      subject_cums[key][i] += subject_cums[key][i-1]

  return subject_cums


def subject_cumulatives_hours(user_data):
  subject_cums = subject_cumulatives(user_data)
  for key in subject_cums.keys():
    for i in range(len(subject_cums[key])):
      subject_cums[key][i] = subject_cums[key][i].total_seconds() / 3600

  return subject_cums


def subject_session_counts(user_data):
  '''Count the total number of sessions for each subject
  '''
  totals = {subject : 0 for subject in user_data['subjects']}

  for session in user_data['sessions']:
    totals[session['subject']] += 1

  return totals


def average_session_lengths(user_data):
  '''Return the average duration of a session for a 
  '''
  sub_totals = subject_totals(user_data)
  session_counts = subject_session_counts(user_data)
  for key in sub_totals.keys():
    sub_totals[key] /= session_counts[key]

  return sub_totals


def average_session_lengths_hours(user_data):
  lengths = average_session_lengths(user_data)
  for key in lengths.keys():
    lengths[key] = lengths[key].total_seconds() / 3600

  return lengths

def longest_sessions(user_data):
  '''
  '''
  longest_sessions = {subject : timedelta() for subject in user_data['subjects']}

  for session in user_data['sessions']:
    if session['end'] > longest_sessions[session['subject']]:
      longest_sessions[session['subject']] = session['end']

  return longest_sessions


def longest_sessions_hours(user_data):
  longests = longest_sessions(user_data)
  longests_hours = {}
  for key in longests.keys():
    longests_hours[key] = longests[key].total_seconds() / 3600

  return longests_hours
