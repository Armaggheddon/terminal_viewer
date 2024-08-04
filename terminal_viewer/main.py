import os
import argparse
from .display import Display

def is_file(path):
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"{path} is not a file")
    return path

def is_dir(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"{path} is not a directory")
    return path

def get_parser():
    parser = argparse.ArgumentParser(
        prog="terminal_viewer",
        description="Display media in terminal",
        epilog="Text at the bottom of the help"
        )
    parser.add_argument(
        "-s", "--source", required=False, 
        type=is_file,
        help="Path or paths to media files to display. If multiple paths are provided, they will be displayed in sequence", 
        nargs="+"
        )
    parser.add_argument(
        "-f", "--folder", required=False,
        type=is_dir,
        help="Path to folder or folders containing media files to display. If multiple paths are provided, they will be displayed in sequence",
        nargs="+"
        )
    parser.add_argument(
        "-g", "--grayscale", required=False,
        default=False,
        help="Display media in grayscale",
        action="store_true",
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    display = Display(
        media_paths=args.source, 
        folders=args.folder, 
        grayscale=args.grayscale)
    display.show()