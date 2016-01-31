#!/usr/bin/env python3

import analytics
from datetime import timedelta

db = analytics.get_db_connection()
user = analytics.get_document(db,222)
analytics.convert_start_delta(user)
hmcm = analytics.heirarchical_markov_chain_model(user,timedelta(days=1),10)

new_sessions = []
for x in range(500):
    new_sessions.append(mcmc_simulation(user,hmcm,timedelta(days=1),timedelta(minutes=5),7))
