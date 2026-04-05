import argparse
from importlib import resources


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--azanfiles", help="Path to the azan wav files to play", required=False
    )
    args = parser.parse_args()

    return args


args = parse_args()


def azan_files() -> str:
    if args.azanfiles is not None:
        return args.azanfiles
    else:
        return str(resources.files("bilal").joinpath("audio_files"))
