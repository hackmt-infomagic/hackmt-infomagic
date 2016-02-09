#!/usr/bin/env python3

import analytics
from datetime import timedelta

db = analytics.get_db_connection()
user = analytics.get_document(db,222)
analytics.convert_start_delta(user)
hmcm = analytics.heirarchical_markov_chain_model(user,timedelta(days=1),10)

cumulatives = []
for x in range(100):
    ## Iterations
    user = analytics.get_document(db,222)
    analytics.convert_start_delta(user)
    user['sessions'] += analytics.mcmc_simulation(user,hmcm,timedelta(days=1),timedelta(minutes=5),7)
    cumulatives.append(analytics.cumulative(user))
