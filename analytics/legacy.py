#---Module Imports---
from os import path, environ, SEEK_SET, SEEK_END
from typing import List, Tuple, Set, Dict, Iterator
from datetime import datetime, date, time, timedelta
#--------------------

# Changing either of the following values will require a new 
# log file to be used, as these values affect the specific 
# layout of the log file.
NUM_SUBJECT_BYTES  = 25 # type: int
NUM_TIME_BYTES     = 14 # type: int

# These values indicate how many bytes certain parts of the
# log file will occupy. They are used for writing and indexing
# to specific places in the log file.
NUM_STATUS_BYTES = NUM_SUBJECT_BYTES + NUM_TIME_BYTES + 6      # type: int
NUM_ENTRY_BYTES  = NUM_SUBJECT_BYTES + 2 * NUM_TIME_BYTES + 5  # type: int

# The names of the log file and the subject file within the 
# directory specified in STUDYPATH
LOG_FILE     = 'study_log.csv'  # type: str
SUBJECT_FILE = 'subjects.csv'   # type: str

# Messages to the user
NOT_STUDYING     = 'You are not studying right now.'      # type: str
INVALID_SUBJECT  = '{:s} is an invalid subject.'          # type: str
FINISH_CURRENT   = 'Finish the current session first.'    # type: str
SUBJECT_TOO_LONG = 'That subject name is too long (max = {:d})' # type: str


def getStudyPath() -> str:
  '''Returns the path to the directory used by this module.
  '''
  return environ.get('STUDYPATH').rstrip('/')


def getLogPath() -> str:
  '''Returns the path to the log file.
  '''
  return getStudyPath() + '/' + LOG_FILE


def getSubjectPath() -> str:
  '''Returns the path to the file containing valid subjects.
  '''
  return getStudyPath() + '/' + SUBJECT_FILE


def newLogFile() -> str:
  return statusString(False, 'none', 0)


def newSubjectFile() -> str:
  return 'math\nphysics\nprogramming\nrandom\n'


def backup():
  '''Backup the current study log.
  '''
  # Get the current datetime
  dt = datetime.now()

  # generate name of backup file
  bname = 'study_log_{:d}_{:d}_{:d}_{:d}_{:d}_{:d}.backup'.format(dt.month, dt.day, dt.year, dt.hour, dt.minute, dt.second)

  # Open study log and the backup file.
  f = open(getLogPath())
  g = open(getStudyPath() + '/backups/' +  bname, 'w+')

  # Copy study data into backup file
  g.write(f.read())

  # Close files
  f.close()
  g.close()


def entryString(subject: str, start: int, end: int) -> str:
  '''Create the string to be used when a study session is logged.
  '''
  pat = '{{:{:d}s}}, {{:{:d}d}}, {{:{:d}d}}\n'.format(NUM_SUBJECT_BYTES, NUM_TIME_BYTES, NUM_TIME_BYTES)
  return pat.format(subject, start, end)


def statusString(status: bool, subject: str, time: int) -> str:
  '''Create a string to represent status information in the log file.
  '''
  statusByte = 1 if status else 0 # type: int
  pat = '{{:d}}, {{:{:d}s}}, {{:{:d}d}}\n'.format(NUM_SUBJECT_BYTES, NUM_TIME_BYTES)
  return pat.format(statusByte, subject, time)


def start(f, subject: str, time: int) -> None:
  '''Log the start of a study session.
  '''
  f.seek(0, SEEK_SET) # beginning
  f.write(statusString(True, subject, time))


def stop(f, end: int) -> None:
  '''Log the end of a study session.
  '''
  # Get current status
  status = getStatus(f)
  subject = status[1]
  start = status[2]

  # Reset status
  f.seek(0, SEEK_SET) # beginning
  f.write(statusString(False, 'none', 0))

  # Log new entry
  f.seek(0, SEEK_END) # end
  f.write(entryString(subject, start, end))


def abort(f) -> None:
  '''Abort the current study session.
  '''
  # Reset status
  f.seek(0, SEEK_SET) # beginning
  f.write(statusString(False, 'none', 0))


# UNDER CONSTRUCTION
def insert(log_path: str, sub: str, start: int, end: int) -> None:
  '''Insert an entry in the log file.
  '''
  if not validSubject(subjectPath, sub):
    return None

  with open(log_path, 'r+') as f:
    entries = getEntries(f)
    if len(entries) == 0:
      entries.append((sub, start, end))
    else:
      if (end <= entries[0][1]):
        f.seek(NUM_STATUS_BYTES)
        f.write()
        f.write('\n'.join([]))


def validSubject(path: str, subject: str) -> bool:
  with open(path, 'r') as f:
    subjects = f.readlines()  # type: List[str]
    return True if (subject.lower() + '\n') in subjects else False


def addSubject(sub_path: str, new_sub: str) -> None:
  '''Adds a new subject to the subject file.

     Checks if the subject is already in the subject file
     and does nothing if it is.
  '''
  with open(sub_path, 'r+') as f:
    curr_subs = [line.rstrip('\n') for line in f]
    if new_sub not in curr_subs:
      f.seek(0, SEEK_END) # end
      f.write(new_sub + '\n')


def renameSubject(sub_path, old_sub_name, new_sub_name):
  '''Renames the given subject if it exists.
  '''

  # If the old subject name is invalid, abort
  if not validSubject(sub_path, old_sub_name):
    raise Exception('Invalid Subject')

  # Update the study log file
  with open(getLogPath(), 'r+') as f:
    new_log_data = [ ((new_sub_name, entry[1], entry[2]) if entry[0] == old_sub_name else entry) for entry in getEntries(f) ]
    setEntries(f, new_log_data)

  # Remove old name and add new name to subject list
  subject_list = getSubjects()
  subject_list.remove(old_sub_name)
  subject_list.append(new_sub_name + '\n')

  # Truncate the subject file and write back the new subject list
  with open(sub_path, 'w') as sub_file:
    sub_file.write('\n'.join(subject_list))


def removeSubject(sub_path: str, sub: str) -> None:
  '''Removes a subject from the subject file.

     Pre: sub is an entry in the subject file
     Pre: sub does not appear in the log file
  '''
  with open(sub_path, 'r+') as f:
    lines = f.readlines()
    lines.remove(sub + '\n')
    new_text = ''.join(lines)
    f.truncate(len(new_text))
    f.seek(0, SEEK_SET)
    f.write(new_text)

# UNDER CONSTRUCTION
def mergeSubjects(leaving: str, remaining: str) -> None:
  '''Assign all entries from one subject to another
  '''

  with open(getSubjectPath(), 'r+') as f:
    lines = f.readlines()

    # Check that subjects are valid
    if (leaving.lower() + '\n') not in lines or (remaining.lower() + '\n') not in lines:
      raise Exception('Invalid Subject')

    # Remove the old subject from the subject list
    lines.remove(leaving + '\n')

    # Write the new subject list back to the subject file
    new_text = ''.join(lines)
    f.truncate(len(new_text))
    f.seek(0, SEEK_SET)
    f.write(new_text)

  # Change the subject names in the log file
  with open(getLogPath(), 'r+') as f:
    entries = getEntries(f)

    new_entries = ((remaining, e[1], e[2]) if e[0] == leaving else e for e in entries)

    # Write the new entries back to the log file
    setEntries(f, new_entries)


def getSubjectsFromPath(sub_path: str) -> List[str]:
  '''Returns the valid subjects as a list.
  '''
  with open(sub_path, 'r') as f:
    subs = [line.rstrip('\n') for line in f]

  return subs

def getSubjects() -> List[str]:
  '''
  '''
  return getSubjectsFromPath(getSubjectPath())

def getStatus(f) -> Tuple[bool, str, int]:
  '''Returns the status and subject being studied.
  
  >>> getStatus('notStudying.log')
  (False, 'none', 0)
  
  >>> getStatus('isStudying.log')
  (True, 'math', 147567098)
  '''

  f.seek(0, SEEK_SET) # beginning  
  info = f.readline().split(',')   # type: List[str]
  return (bool(int(info[0])), info[1].strip(), int(info[2]))


def parseEntry(line: str) -> Tuple[str, int, int]:
  x = line.split(',')
  return (x[0].strip(), int(x[1]), int(x[2]))


def getEntries(f) -> List[Tuple[str, int, int]]:
  '''
  '''
  f.seek(NUM_STATUS_BYTES)
  entries = [parseEntry(line.rstrip('\n')) for line in f.readlines()]

  return entries

def setEntries(f, entries: List[Tuple[str, int, int]]) -> None:
  '''
  '''
  new_text = ''.join((entryString(e[0], e[1], e[2]) for e in entries))
  f.truncate(NUM_STATUS_BYTES + len(new_text))
  f.seek(NUM_STATUS_BYTES)
  f.write(new_text)

def entriesBackwards(log_path: str) -> Iterator[Tuple[str, int, int]]:
  '''Iterate through the entries backwards (most recent first)
  '''
  with open(log_path, 'r') as f:
    f.seek(NUM_STATUS_BYTES, SEEK_SET) # first entry
    text = f.read()

  pos = len(text) - NUM_ENTRY_BYTES
  while pos >= 0:
    yield parseEntry(text[pos : pos + NUM_ENTRY_BYTES])
    pos -= NUM_ENTRY_BYTES


# UNDER CONSTRUCTION
def checkInterval(entries: List[Tuple[str, int, int]], start: int, end: int) -> bool:
  '''Checks if an interval conflicts with any entry from a list.

     Assumes that the entry list is valid and sorted.
  '''
  if end >= start:
    raise Exception('interval of zero length')

  last = len(entries) - 1

  if end <= entries[0][1] or start >= entries[last][2]:
    return True
  else:
    for i in range(last):
      if start >= entries[i][2] and end <= entries[i+1][1]:
        return True

  return False


def dataIsValid(study_path: str, sub_path: str) -> bool:
  '''
  '''
  subs = set(getSubjectsFromPath(sub_path))  # type: Set[str]

  with open(study_path, 'r') as f:
    f.seek(NUM_STATUS_BYTES, SEEK_SET)  # first entry
    for line in f:
      e = parseEntry(line.rstrip('\n'))
      if e[2] < e[1] or e[0] not in subs:
        return False

  # Everything OK
  return True

def startOfNextDay(dt):
  '''
  '''
  return (dt + timedelta(days=1)).replace(hour = 0, minute = 0, second = 0, microsecond = 0)

def startOfNextMonth(dt):
  '''
  '''
  start_month = dt.month
  res = dt.replace()  # new datetime object
  while res.month == start_month:
    res += timedelta(days=28)
  return res.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def startOfNextYear(dt):
  '''
  '''
  start_year = dt.year
  res = dt.replace()  # new datetime object
  while res.year == start_year:
    res += timedelta(days=365)
  return res.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


class Task(object):
  '''Represents something that can occupy one's time.
  '''

  def __init__(self):
    pass


class Entry(object):
  '''
  '''

  @classmethod
  def fromTimestamps(cls, task, start, end):
    '''
    '''
    return cls(task, datetime.fromtimestamp(start), datetime.fromtimestamp(end))


  def __init__(self, task, start, end):
    self.task  = task
    self.start = start
    self.end   = end


  def delta(self):
    return self.end - self.start


class GroupedData(object):
  '''
  '''

  def __init__(self, raw_entries, grouping = 'day'):

    self.groups   = ['day', 'month', 'year']

    if len(raw_entries) == 0:
      raise Exception('No data')

    if grouping not in self.groups:
      raise Exception('Invalid grouping: {}'.format(grouping))

    entries       = self.convert_raw_entries(raw_entries)
    self.grouping = grouping
    self.data     = self._groupEntries(entries)
    self.bounds   = [(self.startOfGroup(d[0][1]), self.startOfNextGroup(d[0][1])) for d in self.data]
    self.stats    = {}


  def convert_raw_entries(self, raw_entries: List[Tuple[str, int, int]]):
    '''Convert from timestamps to datetimes.
    '''

    res = []
    for re in raw_entries:
      start = datetime.fromtimestamp(re[1])
      end   = datetime.fromtimestamp(re[2])
      res.append((re[0], start, end - start))

    return res

  def sameGroup(self, dt1, dt2):
    '''Returns True iff the datetimes fall in the same group based on the current grouping.
    ''' 
    if self.grouping == 'day':
      res = (dt1.year == dt2.year) and (dt1.month == dt2.month) and (dt1.day == dt2.day)
    elif self.grouping == 'month':
      res = (dt1.year == dt2.year) and (dt1.month == dt2.month)
    elif self.grouping == 'year':
      res =  dt1.year == dt2.year

    return res


  def startOfGroup(self, dt):
    '''
    '''
    if self.grouping == 'day':
      res =  datetime.combine(dt.date(), time())
    elif self.grouping == 'month':
      res = dt.replace(day=1)
    elif self.grouping == 'year':
      res = dt.replace(month=1, day=1)

    return res


  def startOfNextGroup(self, dt):
    '''
    '''
    if self.grouping == 'day':
      res = startOfNextDay(dt)
    elif self.grouping == 'month':
      res = startOfNextMonth(dt)
    elif self.grouping == 'year':
      res = startOfNextYear(dt)

    return res


  def _groupEntries(self, es: List[Tuple[str, datetime, timedelta]]) -> List[List[Tuple[str, datetime, timedelta]]]:
    '''Group entries by month, day, or year.

    All the issues with edge cases arise from the fact that I'm working with
    timestamps instead of durations.

    A session cannot end or start on the last instant of a group because our
    timestamps only have a resolution of seconds.
    '''
    if len(es) == 0:
      return es

    res = []

    # Initialize loop variables
    start = es[0][1]                 #type: datetime
    end   = start + es[0][2]         #type: datetime
    curr  = start                    #type: datetime
    nb    = self.startOfNextGroup(curr)    #type: datetime
    curr_entries = []                      #type: List[Tuple[str, datetime, datetime]]

    # Handle the first session
    while nb <= end:
      res.append((e[0][0], curr, nb - curr))
      curr = nb
      nb = self.startOfNextGroup(curr)

    # If a session ends on a boundary, then end == curr at this point. 
    # We choose to ignore the empty session that results from splitting.
    if curr < end:
      curr_entries.append((es[0][0], curr, end - curr))
      curr = end

    # Handle the remaining sessions
    # Invariants:
    #  - curr <= end
    #  - curr <= nb
    #  - all times < self.startOfGroup(curr) are in res
    #  - all times such that (self.startOfGroup(curr) <= time < curr) are in curr_entries
    #  - comp(curr, nb) is true
    #  - if curr > self.startOfGroup(curr), then curr_entries is non-empty (???)
    for e in es[1:]:
      start = e[1]
      end   = start + e[2]

      # Check if this entry starts in a new group
      if not self.sameGroup(curr, start):
        if curr > self.startOfGroup(curr):
          res.append(curr_entries)
          curr_entries = []
        nb = self.startOfNextGroup(start)

      curr = start

      # Check if this entry starts but does not end today
      while nb <= end:
        curr_entries.append((e[0], curr, nb - curr))
        res.append(curr_entries)
        curr_entries = []
        curr = nb
        nb = self.startOfNextGroup(curr)

      # If a session ends on the first instant of the next group, then
      # splitting will result in a session of length zero. We choose
      # to ignore this null session.
      if curr < end:
        curr_entries.append((e[0], curr, end - curr))
        curr = end

    # Add any remaining entries to the result
    res.append(curr_entries)

    return res


  def regroup(self, grouping):

    if grouping not in self.groups:
      raise Exception('Invalid group')
    elif grouping == self.grouping:
      # Regrouping to the current group is a no-op
      return

    # Update the grouping
    self.grouping = grouping

    # Reset the stats
    self.stats = {}

    # Create a flat view of the entries for regrouping
    flat = []
    for group in self.data:
      for entry in group:
        flat.append(entry)

    # Regroup the data
    self.data = self._groupEntries(flat)

    # Reset the bounds
    self.bounds = [(self.startOfGroup(d[0][1]), self.startOfNextGroup(d[0][1])) for d in self.data]


  def __iter__(self):
    '''Iterate over the groupings.
    '''
    return iter(self.data)


  def __getitem__(self, i):
    '''Index into the sequence of groupings.
    '''
    return self.data[i]

  def __len__(self):
    '''Return the number of groupings.
    '''
    return len(self.data)

  def _addStat(self, stat, computeStat):
    '''Computes and stores a new statistic for each group.
    '''
    self.stats[stat] = []
    for g in self.data:
      self.stats[stat].append(computeStat(g))


  def computeStat(self, stat):
    '''Compute the given statistic.
    '''
    if stat not in self.stats:
      if (stat == 'sum'):
        self._addStat('sum', sumEntries)

      elif (stat == 'cumulative_sum'):
        # Compute sum if we haven't already
        if 'sum' not in self.stats:
          self._addStat('sum', sumEntries)

        # Compute cumulative_sum using sum
        self.stats['cumulative_sum'] = [self.stats['sum'][0]]
        for i in range(1, len(self.data)):
          self.stats['cumulative_sum'].append(self.stats['sum'][i] + self.stats['cumulative_sum'][i-1])

      elif (stat == 'subject_totals'):
        self._addStat('subject_totals', subjectTotals)

      elif (stat == 'longest_session'):
        self._addStat('longest_session', longestSession)

      else:
        raise Exception('invalid statistic: {:s}'.format(stat))


# ------ End of GroupedData ------

def sumEntries(es: List[Tuple[str, datetime, timedelta]]) -> timedelta:
  '''Return the total duration of the given study sessions.
  '''
  sum = timedelta()  # type: timedelta
  for e in es:
    sum += e[2]

  return sum


def subjectTotals(sessions: List[Tuple[str, datetime, timedelta]]) -> Dict[str, timedelta]:
  '''Returns the total time spent studying each subject as a dict.
  '''
  res = {}

  # Sum sessions using timedelta
  for s in sessions:
    res[s[0]] = res.get(s[0], timedelta()) + s[2]

  return res

# TODO
# ( ) - Think about normalization error when too few bins are used.
#       Probability can exceed one in these cases
def averageDensity(gdata, num_bins) -> List[float]:
  '''Compute average density based on group data.
  '''

  bins = [0 for _ in range(num_bins)]
  num_groups = len(gdata)

  for i in range(len(gdata)):
    start = gdata.bounds[i][0]
    end   = gdata.bounds[i][1]
    length = end - start
    for session in gdata[i]:
      start_bin = int(((session[1] - start) / length) * num_bins)
      end_bin   = int((((session[1] + session[2]) - start) / length) * num_bins)

      if end_bin == num_bins:
        end_bin -= 1

      for b in range(start_bin, end_bin + 1):
        bins[b] += 1

  # Normalize the bins
  for i in range(len(bins)):
    bins[i] /= num_groups

  return bins


def subjectDensities(gdata, num_bins) -> List[float]:
  '''Compute the density for each subject separately.
  '''

  subject_bins = {}
  num_groups = len(gdata)

  for i in range(len(gdata)):
    start = gdata.bounds[i][0]
    end   = gdata.bounds[i][1]
    length = end - start
    for session in gdata[i]:
      start_bin = int(((session[1] - start) / length) * num_bins)
      end_bin   = int((((session[1] + session[2]) - start) / length) * num_bins)

      if end_bin == num_bins:
        end_bin -= 1

      # Ensure that subject_bins has a place for this session's subject.
      subject_bins[session[0]] = subject_bins.get(session[0], [0 for _ in range(num_bins)])

      # Fill the bins only for the session's subject
      for b in range(start_bin, end_bin + 1):
        subject_bins[session[0]][b] += 1

  # Normalize each subject independently
  for sub in subject_bins:
    shift  = min(subject_bins[sub])
    factor = max(subject_bins[sub]) - shift
    for i in range(len(subject_bins[sub])):
      subject_bins[sub][i] -= shift
      subject_bins[sub][i] /= factor

  return subject_bins


def longestSession(sessions: List[Tuple[str, datetime, timedelta]]) -> timedelta:
  '''Return the duration of the longest session from the list.
  '''
  max = timedelta()
  for s in sessions:
    if s[2] > max:
      max = d

  return max


def longestStreak(ds):
  '''
  '''
  if len(ds) == 0:
    return 0

  curr = 1
  max = 1

  for i in range(1, len(ds)):
    if ds[i][0] == (ds[i-1][0] + timedelta(days=1)):
      curr += 1
    else:
      if curr > max:
        max = curr
      curr = 1

  return max


