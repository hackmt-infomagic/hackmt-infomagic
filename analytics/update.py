import analytics


data_generators = [
  ('global_cumulative'       , analytics.cumulative_hours),
  ('average_session_lengths' , analytics.average_session_lengths_hours),
  ('longest_sessions'        , analytics.longest_sessions_hours),
  ('subject_totals'          , analytics.subject_totals_hours),
  ('subject_session_counts'  , analytics.subject_session_counts),
  ('subject_cumulatives'     , analytics.subject_cumulatives_hours),
  ('global_end'              , analytics.global_end_string),
  ('global_start'            , analytics.global_start_string)
]

# Get a connection to the database
db = analytics.get_db_connection()

# Get user data
user_data = analytics.get_document(222)
analytics.convert_start_delta(user_data)

for gen in data_generators:
  db.Users.update_one(
  {'user_id': 222},
  {'$set' : {'stats.{:s}'.format(gen[0]): gen[1](user_data)}}
  )


