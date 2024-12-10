import subprocess


def run():
    subprocess.run(['semantic-release'], check=True)
