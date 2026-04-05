import argparse
from importlib import resources

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--calenderpath', help='Path to the azan calendar folder', required=False)
    parser.add_argument('-a','--azanfiles', help='Path to the azan wav files to play', required=False)
    args = parser.parse_args()

    return args

args = parse_args()

def calendar_path() -> str:
    if args.calenderpath is not None:
        return args.calenderpath
    else:
        return str(resources.files('bilal').joinpath('prayer_times'))

def azan_files() -> str:
    if args.azanfiles is not None:
        return args.azanfiles
    else:
        return str(resources.files('bilal').joinpath('audio_files'))
