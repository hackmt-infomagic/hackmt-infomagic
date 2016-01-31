import analytics

# subject cumulative

data_generators = [
  ('global_cumulative'       , analytics.cumulative_hours),
  ('average_session_lengths' , analytics.average_session_lengths_hours),
  ('subject_totals'          , analytics.subject_totals_hours),
  ('subject_session_counts'  , analytics.subject_session_counts),
  ('subject_cumulatives'     , analytics.subject_cumulatives_hours)
]

# Get a connection to the database
db = analytics.get_db_connection()

# Get user data
user_data = analytics.get_document(222)
analytics.convert_start_delta(user_data)

# update all data in one group transaction
db['Users'].update_one(
{'user_id': 222},
{'$set' : {'stats.{:s}'.format(gen[0]) : gen[1](user_data)} for gen in data_generators}
)
