#!/usr/bin/env python3

import numpy
from datetime import datetime, timedelta
from pymongo import MongoClient
from math import ceil
from sklearn.neighbors import KernelDensity
from sklearn import cluster, datasets
from sklearn.neighbors import kneighbors_graph
from sklearn.decomposition import PCA
from copy import deepcopy

def get_db_connection():
    client = MongoClient('mongodb://hackmt-infomagic:hackmt1!@ds051655.mongolab.com:51655/hackmt-infomagic')
    db = client['hackmt-infomagic']
    return db

def get_document(db,user_id):
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


def user_total(user_data):
  '''Return the total number of hours a user has studied'''

  total = timedelta()
  for session in user_data['session']:
    total += session.end

  return total


def calc_probabilities(subjects,sessions):
    '''Calculate global probabilities of events given a list of sessions - including gaps'''
    ## Setup timestamps as datetime-timedelta
    ## convert_start_delta(user_data)

    subjects = subjects + ['Not Tracked']
    n = len(subjects)
    state_probabilities = numpy.zeros(n)
    if len(sessions) < 2:
        if len(sessions) == 1:
            state_probabilities[subjects.index(sessions[0]['subject'])] = 1.0
        else:
            state_probabilities[len(subjects)-1] = 1.0
        return({'P':state_probabilities,
                'from':None,
                'to':None,
                'joint':None})
    
    ## Using this to avoid divide-by-zero, for now...
    transition_probabilities = numpy.zeros((n,n))+0.00000001
    lastend = sessions[0]['start']
    total = 0.0
    gaps = []

    ## Calculate overall state probabilities and gap lengths
    for session in sessions:
        session_time = session['end']
        gap_time = session['start'] - lastend
        state_probabilities[subjects.index(session['subject'])] += session_time.total_seconds()
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
    ## to_start_end(user_data)
    ## to_raw_timestamps(user_data)

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


def subject_session_counts(user_data):
  '''
  '''
  # Initialize a dict of subject -> total
  totals = {subject : 0 for subject in user_data['subjects']}

  for session in user_data['sessions']:
    totals[session['subject']] += 1

  return totals


def average_session_length(user_data):
  '''
  '''
  sub_totals = subject_totals(user_data)
  session_counts = subject_session_counts(user_data)
  for key in sub_totals.keys():
    sub_totals[key] /= session_counts[key]


def calc_binned_probabilities(user_data, bin_duration):
    results = []
    for data in bin_data(user_data,bin_duration):
        results.append(calc_probabilities(user_data['subjects'],data))
    return(results)

def cluster_probabilities(binned_probabilities,n_clust):
    patterns = numpy.zeros((len(binned_probabilities),len(binned_probabilities[0]['P'])))
    for x in range(len(binned_probabilities)):
        patterns[x,:] = binned_probabilities[x]['P']
    ## patterns = patterns[:,:-1]

    ## connectivity matrix for structured Ward
    connectivity = kneighbors_graph(patterns, n_neighbors=10, include_self=False)
    ## make connectivity symmetric
    connectivity = 0.5 * (connectivity + connectivity.T)
    ## spectral = cluster.SpectralClustering(n_clusters=10,eigen_solver='arpack',affinity="nearest_neighbors")
    ward = cluster.AgglomerativeClustering(n_clusters=n_clust, linkage='ward',connectivity=connectivity)
    ward.fit(patterns)
    assignments = ward.labels_.astype(numpy.int)

    probabilities = numpy.zeros(patterns.shape)
    for x in range(n_clust):
        temp = patterns[assignments==x,:].mean(axis=0)
        probabilities[x,:] = temp / numpy.linalg.norm(temp)

    transitions = numpy.zeros((n_clust,n_clust))+0.00000001
    for x in range(len(assignments)-1):
        transitions[assignments[x],assignments[x+1]] += 1.0
    transitions /= transitions.sum()

    ## pca = PCA(n_components=2)
    ## pca = pca.fit(patterns[:,:-1]).transform(patterns[:,:-1])

    return({'P':probabilities,'joint':transitions,'assignments':assignments,'n_clust':n_clust,'patterns':patterns})

def heirarchical_markov_chain_model(user_data,bin_duration,n_clust):
    fine_grained = calc_binned_probabilities(user_data,bin_duration)
    coarse_grained = cluster_probabilities(fine_grained,n_clust)
    return({'fine':fine_grained,'coarse':coarse_grained})

## course_duration is anticipated to be the bin size from the                                                                                                                                                     
## call to the hmcm code.                                                                                                                                                                                        
## fine_duration is up to the user, but should be a reasonably                                                                                                                                                    
## smaller (~100 times) than the coarse duration.
def mcmc_simulation(user_data,hmcm,coarse_duration,fine_duration,coarse_iterations):
    '''Generate a possible future from the given hmcm model'''
    subjects = user_data['subjects'] + ["not tracked"]
    scenario_time = user_data['sessions'][-1]['start'] + user_data['sessions'][-1]['end']
    current_scenario = hmcm['coarse']['assignments'][-1]
    current_state = 0
    fine_bins = int(ceil(coarse_duration.total_seconds() / fine_duration.total_seconds()))

    coarse_probs = hmcm['coarse']['P']
    coarse_tprobs = hmcm['coarse']['joint']
    coarse_assignments = hmcm['coarse']['assignments']
    
    ## Generate a possible scenario                                                                                                                                                                                
    new_sessions = []
    for iteration in range(coarse_iterations):
        ## Select a daytime scenario from -last- daytime                                                                                                                                                           
        ## probabilities, then continue from there using                                                                                                                                                           
        ## the transition probabilities                                                                                                                                                                            
        t_probs = coarse_tprobs[current_scenario,:]
        t_probs /= t_probs.sum()
        current_scenario = numpy.asscalar(numpy.random.choice(range(len(t_probs)), 1, p=t_probs))
        ## Find the set of bins that are in this cluster
        possible_states = numpy.array(range(len(coarse_assignments)))[coarse_assignments==current_scenario]
        ## Use dot-product distance to create probabilities of selecting
        distance = numpy.zeros(len(possible_states))
        mean = coarse_probs[current_scenario,:]
        for x in range(len(possible_states)):
            s_probs = hmcm['fine'][possible_states[x]]['P']
            distance[x] = numpy.inner(mean,s_probs)+1.0
        distance /= distance.sum()
        ## Obtain the state!
        current_state = possible_states[numpy.asscalar(numpy.random.choice(range(len(distance)), 1, p=distance))]
        s_probs = hmcm['fine'][current_state]['P']
        t_probs = hmcm['fine'][current_state]['to']
        
        ## Simulate in the scenario window...
        ## This part is not yet correct...
        subnums = numpy.random.choice(range(len(s_probs)), fine_bins, p=s_probs)
        current_time = scenario_time
        duration = fine_duration
        for x in range(len(subnums)):
            subject = subjects[subnums[x]]
            if subject != 'not tracked':
                mysession = {'subject':subject,'start':current_time,'end':fine_duration,'tags':[]}
                new_sessions.append(deepcopy(mysession))
            current_time += fine_duration
        
        ## Update scenario_time
        scenario_time += coarse_duration
    return(new_sessions)
