#!/usr/bin/env python

import argparse

# Read in the command line arguments
parser = argparse.ArgumentParser(
    description='Run uHTRtool over a range of crates, slots, and feds.',
)

parser.add_argument(
    '--crates',       # The option on the command line
    dest='crates',    # The variable to store the result in
    metavar='crate',  # The variable to display in the help menu
    nargs='+',        # If this flag is given, require one or more arguments
    type=int,         # Convert arguments using int()
    required=True,    # This flag must be present
    # The help message to display when this program is called with -h or --help
    help="A space separated list of crates to run over. Specifying at least one is required.",
)
parser.add_argument(
    '--slots',
    dest='slots',
    metavar='slot',
    nargs='+',
    type=int,
    help="A space separated list of slots to run over. If none are given than all slots are run over.",
)
parser.add_argument(
    '--feds',
    dest='feds',
    metavar='FED',
    nargs='+',
    type=int,
    help="A space separated list of FEDs to read. If none are given than all FEDs are read out.",
)

args = parser.parse_args()
