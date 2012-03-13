reserved_tags = ['open', 'closed', 'started']

command_usage_help = {
    'init': {
        'usage': 'mut init <repo_name>',
        'desc': 'Initialize repository.',
        'shortdesc': 'initialize repository',
        'notes': [
            'if remote, specify hostname/repository.',
            'install public key on host to prevent having to re-enter password'
        ]
    },
    'add-remote': {
        'usage': 'mut add-remote <repo_uri> [remote_name]',
        'desc': 'Add remote repository.',
        'shortdesc': 'add remote repository',
        'notes': [
            'repo_uri should be in format: [user@]host:directory',
            'remote_name optionally aliases the remote hostname'
        ]
    },
    'drop-remote': {
        'usage': 'mut drop_remote <remote_name>',
        'desc': 'Drop remote repository host.',
        'shortdesc': 'drop remote repository'
    },
    'switch': {
        'usage': 'mut switch <repository>',
        'desc': 'Switch context to <repository>.',
        'shortdesc': 'switch active repository',
        'notes': [
            'if remote, specify hostname/repository'
        ]
    },
    'ls': {
        'usage': 'mut ls [:tag]* [:-tag]*',
        'desc': 'List tasks, optionally filtered by tags (filter is done by intersection, not union).',
        'shortdesc': 'list tasks'
    },
    'add': {
        'usage': 'mut add <desciption> [:tag]* [+priority]',
        'desc': 'Create new task, optionally with tags and priority.',
        'shortdesc': 'create new task'
    },
    'mod': {
        'usage': 'mut mod <id> [:tag]* [:-tag]* [+priority]',
        'desc': 'Modify task attributes.',
        'shortdesc': 'modify task attributes'
    },
    'edit': {
        'usage': 'mut edit <id>',
        'desc': 'Edit task description in default editor.',
        'shortdesc': 'edit task description',
        'notes': [
            'editor is determined by the EDITOR environmental variable (to override this in e.g. bash, add export EDITOR=vim to your .bashrc)'
        ]
    },
    'start': {
        'usage': 'mut start <id>',
        'desc': 'Mark task as started.',
        'shortdesc': 'start task'
    },
    'finish': {
        'usage': 'mut finish <id>',
        'desc': 'Mark task as finished.',
        'shortdesc': 'finish task'
    },
    'rm': {
        'usage': 'mut rm <id>',
        'desc': 'Delete task.',
        'shortdesc': 'delete task'
    }
}