import argparse

from .app.main import run


def nsp_ntfy():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configuration", type=str, required=True)
    parser.add_argument("-nsp", "--nsp_configuration", type=str, required=True)
    arguments = parser.parse_args(None)
    run(arguments)
