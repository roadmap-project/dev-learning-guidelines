import argparse

from cli.commands import test, build, add

commands = {
    'add': add,
    'test': test,
    'build': build,
}

parser = argparse.ArgumentParser(description='Roadmap project CLI')
parser.add_argument(
    'command',
    choices=commands.keys()
)

if __name__ == '__main__':
    args = parser.parse_args()
    f = commands[args.command]
    f()
