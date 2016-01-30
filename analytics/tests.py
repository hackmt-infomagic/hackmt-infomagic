import analytics
from datetime import timedelta

# Test that binning splits properly
def test_bin_splitting(bin_data, duration):
  '''
  '''
  for b in bin_data:
    if len(b) > 0:
      bin_start = b[0]['start']
      bin_end   = bin_start + duration
      for session in b:
        session_start = session['start']
        session_end   = session['start'] + session['end']
        if not ((bin_start <= session_start and session_start <= bin_end) and
                (bin_start <= session_end   and session_end   <= bin_end)): return False

  return True


def test_binning(group_size):
  user_data = analytics.get_document(222)
  analytics.convert_start_delta(user_data)
  bin_data = analytics.bin_data(user_data, group_size)
  return test_bin_splitting(bin_data, group_size)
