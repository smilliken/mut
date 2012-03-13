import os
import ConfigParser

rc_file = os.path.expanduser('~/.mutrc')
if not os.path.exists(rc_file):
    with open(rc_file, 'w') as fp:
        fp.write('''[data]
repo_dir = ~/.mut/
active_repo =''')
config = ConfigParser.SafeConfigParser()
config.read(rc_file)
repo_dir = os.path.expanduser(config.get('data', 'repo_dir'))
try:
    active_repo = config.get('data', 'active_repo')
except ConfigParser.NoOptionError, ex:
    active_repo = None
if not os.path.exists(repo_dir):
    os.mkdir(repo_dir)

def set_active_repo(repo_name):
    config.set('data', 'active_repo', repo_name)
    config.write(open(rc_file, 'w'))