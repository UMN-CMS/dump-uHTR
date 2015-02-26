#!/usr/bin/env python

import argparse
import subprocess

# Backport this function (added in 2.7) for ease of use if it is missing
# Function from:
# https://hg.python.org/cpython/file/d37f963394aa/Lib/subprocess.py#l544
if "check_output" not in dir(subprocess):
    def temp_f(*popenargs, **kwargs):
        r"""Run command with arguments and return its output as a byte string.

        If the exit code was non-zero it raises a CalledProcessError.  The
        CalledProcessError object will have the return code in the returncode
        attribute and output in the output attribute.

        The arguments are the same as for the Popen constructor.  Example:

        >>> check_output(["ls", "-l", "/dev/null"])
        'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

        The stdout argument is not allowed as it is used internally.
        To capture standard error in the result, use stderr=STDOUT.

        >>> check_output(["/bin/sh", "-c",
        ...               "ls -l non_existent_file ; exit 0"],
        ...              stderr=STDOUT)
        'ls: non_existent_file: No such file or directory\n'
        """
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd)
        return output

    subprocess.check_output = temp_f

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
