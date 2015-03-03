#!/usr/bin/env python

import optparse
import subprocess
from tempfile import NamedTemporaryFile
from distutils.spawn import find_executable
from sys import exit

# Set up the text of the script to run on each uHTR
script_commands = (
    "0",
    "LINK",
    "STATUS",
    "QUIT",
    "DTC",
    "STATUS",
    "QUIT",
    "LUMI",
    "QUIT",
    "DAQ",
    "STATUS",
    "QUIT",
    "EXIT",
    "EXIT",
)

# FED map: FED -> Crate
fed_map = {
    1118: 22,
    1120: 29,
    1122: 32,
}

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
            raise subprocess.CalledProcessError(retcode, cmd)
        return output

    subprocess.check_output = temp_f


# Return a IP address from slot and crate
def crate_slot_to_ip(crate, slot):
    ip = "192.168.{crate_num}.{slot_num}".format(
        crate_num=int(crate),
        slot_num=4 * int(slot)
    )

    return ip


# Read in the command line arguments

# We need to split the comma seperated string and make ints of the results, so
# we define a function that we call on each input
def split_callback(option, opt, value, parser):
    split_ints = [int(i) for i in value.split(",")]
    setattr(parser.values, option.dest, split_ints)

usage = """"%prog (--crates crate_num[,...] | --feds fed_num[,...]) [--slots slot_num[,...]]

The one of either the `--crates` flag or the `--feds` flag is mandatory.
"""
parser = optparse.OptionParser(usage=usage)
parser.add_option(
    "--crates",
    type="string",
    action="callback",
    callback=split_callback,
    help="A comma separated list of crates to run over.",
)
parser.add_option(
    "--feds",
    type="string",
    action="callback",
    callback=split_callback,
    help="A comma separated list of FEDs to read.",
)
parser.add_option(
    "--slots",
    type="string",
    action="callback",
    callback=split_callback,
    help="A comma separated list of slots to run over. If none are given than all slots are run over.",
)
options = parser.parse_args()[0]

# We need at least one crate
if not options.crates and not options.feds:
    print("No crates or FEDs given!")
    exit(1)

# If no slots, run on all
if not options.slots:
    options.slots = range(1, 13)

# Call uHTRtool
if find_executable("uHTRtool.exe") is None:
    print("Can not find uHTRtool.exe!")
    exit(2)

# Make a list of the IP address, slots, and crates
is_addresses = []
if options.crates:
    for crate in options.crates:
        for slot in options.slots:
            is_addresses.append((crate_slot_to_ip(crate, slot), crate, slot))

if options.feds:
    for fed in options.feds:
        crate = fed_map.get(fed, None)
        # We skip bad entries or duplicates from the crate menu
        if crate is None or crate in options.crates:
            continue
        for slot in options.slots:
            is_addresses.append((crate_slot_to_ip(crate, slot), crate, slot))

# Sort as its free and this way things will always be in the same order,
# regardless of how the user inputs the devices
is_addresses.sort()

# We write a script to pass to uHTRtool using the -s flag. This file will self
# delete when it goes out of scope (that is, exits the 'with' block)
script_text = "\n".join(script_commands)
with NamedTemporaryFile() as temp_file:
    temp_file.write(script_text)
    temp_file.flush()
    for ip_address, crate, slot in is_addresses:
        header = "========== Crate: {crate_num}; Slot: {slot_num} ==========".format(
            crate_num=crate,
            slot_num=slot
        )
        print header
        command_to_run = ["uHTRtool.exe", ip_address, "-s", temp_file.name]
        output = subprocess.check_output(command_to_run)
        print output
