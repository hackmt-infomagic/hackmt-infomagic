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

def push_stats(user_id,key,data):
    match = get_document(user_id)
    if 'stats' in match.keys():
        match['stats'][key] = data
    else:
        match['stats'] = {key:data}
    match.update()
    
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

