"""Console script for gpm_precipitation_tools."""
import sys
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "gpm_precipitation_tools.cli.main")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
