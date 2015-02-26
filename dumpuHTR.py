#!/usr/bin/env python

import optparse
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

# We need to split the comma seperated string and make ints of the results, so
# we define a function that we call on each input
def split_callback(option, opt, value, parser):
    split_ints = [int(i) for i in value.split(",")]
    setattr(parser.values, option.dest, split_ints)

usage = """"%prog --crates crate_num[,...] [--slots slot_num[,...]] [--feds fed_num[,...]]

The `--crates` flag is mandatory and must include at least one crate to run over.
"""
parser = optparse.OptionParser(usage=usage)
parser.add_option(
    "--crates",
    type="string",
    action="callback",
    callback=split_callback,
    help="A comma separated list of crates to run over. Specifying at least one is required.",
)
parser.add_option(
    "--slots",
    type="string",
    action="callback",
    callback=split_callback,
    help="A comma separated list of slots to run over. If none are given than all slots are run over.",
)
parser.add_option(
    "--feds",
    type="string",
    action="callback",
    callback=split_callback,
    help="A comma separated list of FEDs to read. If none are given than all FEDs are read out.",
)
options = parser.parse_args()[0]

# We need at least one crate
if not options.crates:
    print("No crates given!")
    exit(1)
