import sys
import itertools
import datetime
from signal import signal, SIGPIPE, SIG_DFL 
from dateutil import tz, parser
from termcolor import colored

# fix for exception thrown when running e.g. "mut ls | head -n 1"
# see: http://newbebweb.blogspot.com/2012/02/python-head-ioerror-errno-32-broken.html
signal(SIGPIPE, SIG_DFL)

def _to_local_time(dt):
    dt = dt.replace(tzinfo=tz.tzutc())
    return dt.astimezone(tz.tzlocal())

def _pretty_date(dt):
    if type(dt) in [str, unicode]:
        dt = parser.parse(dt)
    local_dt = _to_local_time(dt)
    local_now = _to_local_time(datetime.datetime.utcnow())
    if abs(local_now - local_dt) < datetime.timedelta(24):
        return local_dt.strftime('%H:%M')
    else:
        return local_dt.strftime('%Y-%m-%d')

def print_tasks(c, task_ids):
    if task_ids:
        rows = []
        for id in task_ids:
            description, priority, created, started, finished = \
                c.execute('SELECT description, priority, created, started, finished FROM task WHERE id = ? ORDER BY priority DESC;', (id,)).fetchone()
            tags = c.execute('SELECT tag FROM tag WHERE task_id = ? ORDER BY tag ASC, id ASC;', (id,))
            tag_str = ' '.join(('[%s]' % tag for tag in tags))
            rows.append({
                'id': id,
                'description': description,
                'priority': priority,
                'created': created,
                'started': started,
                'finished': finished,
                'columns': [
                    str(id),
                    '%s%s %s' % (colored('+%s ' % priority if priority != None else '', 'green'), colored(tag_str, 'yellow'), description)
                ]
            })
        col_widths = [max((len(str(row['columns'][i])) for row in rows)) + 1 for i in xrange(len(rows[0]['columns']))]
        priority = -1
        sys.stdout.write('\033[?7l') # nowrap on
        for row in rows:
            # if row['priority'] != priority:
            #   priority = row['priority']
            #   sys.stdout.write('\n' + colored('Priority %s:' % priority if (priority != None) else 'Non-prioritized:', 'green') + '\n')
            for val, width in itertools.izip(row['columns'], col_widths):
                sys.stdout.write(str(str(val).ljust(width)))
            sys.stdout.write('\n')
        sys.stdout.write('\033[?7h') # nowrap off

def add_tag(c, tag, id):
    result = c.execute('SELECT id FROM tag WHERE tag = ? AND task_id = ?;', (tag, id)).fetchone()
    if not result:
        c.execute('INSERT INTO tag VALUES (null, ?, ?, ?);', (tag, id, datetime.datetime.utcnow()))

def rm_tag(c, tag, id):
    result = c.execute('SELECT id FROM tag WHERE tag = ? AND task_id = ?;', (tag, id)).fetchone()
    if result:
        c.execute('DELETE FROM tag WHERE tag = ? AND task_id = ?;', (tag, id))