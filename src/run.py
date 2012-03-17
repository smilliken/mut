import sys
import datetime
import commands
from constants import reserved_tags, command_usage_help
from config import active_repo

class InvalidUsageException(Exception):
    pass

def usage(command=None):
    if command is None:
        print('''USAGE: mut [command] [--help]\nCOMMANDS:''')
        for command_key in sorted(command_key for command_key in command_usage_help):
            print('%s%s' % (command_key.ljust(30), command_usage_help[command_key]['shortdesc']))
    elif command in command_usage_help:
        print('''USAGE: %s\nDescription: %s''' % (command_usage_help[command]['usage'], command_usage_help[command]['desc']))
        if 'notes' in command_usage_help[command]:
            print('NOTES:')
            for note in command_usage_help[command]['notes']:
                print('* %s' % note)
    else:
        sys.stderr.write('''Unknown command: %s\n''' % command)

def _parse_flags(argv):
    priority, tags, neg_tags, flags = None, [], [], ''
    for arg in argv:
        if arg.startswith('+'):
            if not priority:
                try:
                    priority = int(arg[1:])
                    if priority < 0:
                        raise ValueError()
                except ValueError:
                    raise InvalidUsageException('Priority must be a non-negative integer.')
            else:
                raise InvalidUsageException('Priority can only be specified once.')
        elif arg.startswith(':'):
            tag = arg[2:] if arg.startswith(':-') else arg[1:]
            if not tag or not tag.strip():
                raise InvalidUsageException('Tag cannot be empty string.')
            neg_tags.append(tag) if arg.startswith(':-') else tags.append(tag)
        else:
            raise InvalidUsageException('Unrecognized argument: %s.' % arg)
    return {
        'priority': priority,
        'tags': tags,
        'neg_tags': neg_tags
    }

def main():
    if not sys.argv:
        raise InvalidUsageException()
    argv = sys.argv[1:] # chop off script name as first arg
    try:
        command = argv[0]
    except IndexError:
        raise InvalidUsageException()
    if command == '--help':
        usage()
    elif argv[-1] == '--help':
        usage(command)
    elif command == 'init':
        try:
            repo_name = argv[1]
        except IndexError:
            raise InvalidUsageException('repo_name is required.')
        commands.init(repo_name)
    elif command == 'switch':
        try:
            repo_name = argv[1]
        except IndexError:
            raise InvalidUsageException('repo_name is required.')
        commands.switch(repo_name)
    elif command == 'add-remote':
        try:
            repo_uri = argv[1]
        except IndexError:
            raise InvalidUsageException('repo_uri is required.')
        try:
            remote_name = argv[2]
        except IndexError:
            remote_name = None
        commands.add_remote(repo_uri, remote_name=remote_name)
    elif command == 'drop-remote':
        try:
            remote_name = argv[1]
        except IndexError:
            raise InvalidUsageException('remote_name is required.')
        commands.drop_remote(remote_name)
    elif not active_repo:
        raise InvalidUsageException('no active repository, must init or switch to a repository.')
    elif command == 'ls':
        flags = _parse_flags(argv[1:])
        commands.ls(tags=flags['tags'], neg_tags=flags['neg_tags'])
    elif command == 'add':
        try:
            description = argv[1]
        except IndexError:
            raise InvalidUsageException('Task description is required.')
        flags = _parse_flags(argv[2:])
        if flags['neg_tags']:
            raise InvalidUsageException('Negative tags not valid when adding task.')
        for tag in flags['tags']:
            if tag in reserved_tags:
                raise InvalidUsageException('That tag is reserved. The following tags are automatically attached to tasks: %s.' % ', '.join(reserved_tags))
        commands.add(description, priority=flags['priority'], tags=flags['tags'])
    elif command == 'mod':
        try:
            id = argv[1]
        except IndexError:
            raise InvalidUsageException('id is required.')
        flags = _parse_flags(argv[2:])
        for tag in flags['tags'] + flags['neg_tags']:
            if tag in reserved_tags:
                raise InvalidUsageException('That tag is reserved. The following tags are automatically attached to tasks: %s.' % ', '.join(reserved_tags))
        commands.mod(id, priority=flags['priority'], tags=flags['tags'], neg_tags=flags['neg_tags'])
    elif command == 'edit':
        try:
            id = argv[1]
        except IndexError:
            raise InvalidUsageException('id is required.')
        flags = _parse_flags(argv[2:])
        if flags['priority'] or flags['tags'] or flags['neg_tags']:
            raise InvalidUsageException('Invalid options specified.')
        commands.edit(id)
    elif command == 'start':
        try:
            id = argv[1]
        except IndexError:
            raise InvalidUsageException('id is required.')
        flags = _parse_flags(argv[2:])
        if flags['priority'] or flags['tags'] or flags['neg_tags']:
            raise InvalidUsageException('Invalid options specified.')
        commands.start(id)
    elif command == 'finish':
        try:
            id = argv[1]
        except IndexError:
            raise InvalidUsageException('id is required.')
        flags = _parse_flags(argv[2:])
        if flags['priority'] or flags['tags'] or flags['neg_tags']:
            raise InvalidUsageException('Invalid options specified.')
        commands.finish(id)
    elif command == 'rm':
        try:
            id = argv[1]
        except IndexError:
            raise InvalidUsageException('id is required.')
        flags = _parse_flags(argv[2:])
        if flags['priority'] or flags['tags'] or flags['neg_tags']:
            raise InvalidUsageException('Invalid options specified.')
        commands.rm(id)
    else:
        raise InvalidUsageException('Unrecognized command: %s.' % command)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except InvalidUsageException, ex:
        if str(ex):
            sys.stderr.write('%s\n\n' % ex)
        usage()
        sys.exit(1)