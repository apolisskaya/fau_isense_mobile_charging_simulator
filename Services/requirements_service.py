import subprocess, sys

"""
basic script to automate installation of necessary modules
TODO: move this from current location to independent personal script library
"""


def install(requirement):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', requirement])


def upgrade(requirement):
    subprocess.check_call([sys.executable, '-m', 'pip', 'upgrade', requirement])


if __name__ == 'main':
    with open('requirements.txt') as f:
        requirement_list = f.readlines()
        for r in requirement_list:
            if len(r) > 0:
                install(r)
