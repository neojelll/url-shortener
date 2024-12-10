import subprocess


def run():
    subprocess.run(['poetry', 'run', 'semantic-release'], check=True)
