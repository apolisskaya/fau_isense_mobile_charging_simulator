import subprocess, sys

"""
basic script to automate installation of necessary modules
TODO: move this from current location to independent personal script library
"""


def install_and_upgrade(requirement):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', requirement, '-U'])


def run_requirement_check():
    with open('requirements.txt') as f:
        requirement_list = f.readlines()
        for r in requirement_list:
            if len(r) > 0:
                install_and_upgrade(r)