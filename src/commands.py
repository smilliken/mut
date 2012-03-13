import os
import sys
import subprocess
import datetime
import sqlite3
from urlparse import urlparse
from config import repo_dir, active_repo, set_active_repo
from utils import print_tasks, add_tag, rm_tag

class DBConn(object):

    def __init__(self, repo_name=None):
        self.repo_path = os.path.join(repo_dir, repo_name or active_repo)
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.repo_path)
        self.cursor = self.conn.cursor()
        return self.cursor
    
    def __exit__(self, typ, value, tb):
        self.conn.commit()
        self.cursor.close()

def init(repo_name):
    repo_path = os.path.join(repo_dir, repo_name)
    if os.path.exists(repo_path):
        sys.stderr.write('Repository already exists: %s' % repo_path)
        return
    print('Initializing repository: %s' % repo_name)
    with DBConn(repo_name) as c:
        c.execute('CREATE TABLE task (id INTEGER PRIMARY KEY, description TEXT, priority INTEGER, created_by TEXT, created DATETIME, started DATETIME, finished DATETIME);')
        # TODO: unique constraint on (tag, task_id)
        c.execute('CREATE TABLE tag (id INTEGER PRIMARY KEY, tag TEXT, task_id INTEGER, created_by TEXT, created DATETIME, FOREIGN KEY(task_id) REFERENCES task(id));')
    switch(repo_name)

def add_remote(repo_uri, remote_name=None):
    parsed = urlparse('sfpt://%s' % repo_uri)
    hostname = parsed.hostname
    mount_point = os.path.join(repo_dir, remote_name or hostname)
    if os.path.exists(mount_point):
        sys.stderr.write('''
Unable to add remote repositories: remote_name already in use. 
Specify a remote_name or drop the remote: mut drop-remote %s
''' % remote_name)
        return
    else:
        os.mkdir(mount_point)
    result = subprocess.call('sshfs %s %s -o sshfs_sync -o no_readahead -o cache=no' % (repo_uri, mount_point), shell=True)
    if result == 0:
        print('Remote repositories available in %s.' % mount_point)
    else:
        sys.stderr.write('Unable to mount remote repositories.')

def drop_remote(remote_name):
    mount_point = os.path.join(repo_dir, remote_name)
    if not os.path.exists(mount_point):
        sys.stderr.write('Mount point does not exist: %s' % mount_point)
    result = subprocess.call('fusermount -u %s' % mount_point, shell=True)
    if result != 0:
        sys.stderr.write('Unable to unmount: %s' % mount_point)
        return
    subprocess.call('rm -r %s' % mount_point, shell=True)
    print('Unmounted %s' % remote_name)

def switch(repo_name):
    set_active_repo(repo_name)

def ls(tags=None, neg_tags=None):
    with DBConn() as c:
        query = '''
            SELECT id
            FROM task
            WHERE 1=1
        '''
        params = []
        for tag, include in [(tag, True) for tag in tags] + [(tag, False) for tag in neg_tags]:
            query += '''
                AND ? %s IN (SELECT tag.tag FROM tag WHERE tag.task_id = task.id)
            ''' % ('' if include else 'NOT')
            params.append(tag)
        query += 'ORDER BY priority ASC, id ASC;'
        task_ids = [id for id, in c.execute(query, params).fetchall()]
        print_tasks(c, task_ids)

def add(description, priority=None, tags=None):
    with DBConn() as c:
        id = c.execute('INSERT INTO task VALUES (null, ?, ?, ?, NULL, NULL);', (description, priority, datetime.datetime.utcnow())).lastrowid
        for tag in tags + ['open']:
            add_tag(c, tag, id)
        print_tasks(c, [id])

def mod(id, priority=None, tags=None, neg_tags=None):
    with DBConn() as c:
        if priority or priority == 0:
            c.execute('UPDATE task SET priority = ? WHERE id = ?', (priority, id))
        for tag in (tags or []):
            add_tag(c, tag, id)
        for tag in (neg_tags or []):
            rm_tag(c, tag, id)

def edit(id):
    with DBConn() as c:
        description, = c.execute('SELECT description FROM task WHERE id = ?;', (id,)).fetchone()
        filename = '/tmp/.mut_edit_%s' % id
        with open(filename, 'w') as fp:
            fp.write(description)
        subprocess.call('${EDITOR:-nano} %s' % filename, shell=True)
        with open(filename, 'r') as fp:
            description = fp.read().strip()
        c.execute('UPDATE task SET description = ? WHERE id = ?;', (description, id))
        print_tasks(c, [id])

def start(id):
    with DBConn() as c:
        c.execute('UPDATE task SET started = ? WHERE id = ?;', (datetime.datetime.utcnow(), id))
        add_tag(c, 'started', id)
        print_tasks(c, [id])

def finish(id):
    with DBConn() as c:
        c.execute('UPDATE task SET finished = ? WHERE id = ?;', (datetime.datetime.utcnow(), id))
        rm_tag(c, 'started', id)
        rm_tag(c, 'open', id)
        add_tag(c, 'closed', id)
        print_tasks(c, [id])

def rm(id):
    with DBConn() as c:
        description, = c.execute('SELECT description FROM task WHERE id = ?;', (id,)).fetchone()
        c.execute('DELETE FROM tag WHERE task_id = ?;', (id,))
        c.execute('DELETE FROM task WHERE id = ?;', (id,))
        print('Deleted: %s\t%s' % (id, description))