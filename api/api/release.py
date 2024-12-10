import subprocess


def main():
    subprocess.run(['semantic-release'], check=True)
