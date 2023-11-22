#!/usr/bin/env python3

# ---------------------------------------------------------------------
# Be sure to add the python path that points to the LLDB shared library.
#
# # To use this in the embedded python interpreter using "lldb" just
# import it with the full path using the "command script import"
# command
#   (lldb) command script import ~/lldb/ccsid.py
# ---------------------------------------------------------------------

from __future__ import print_function

import inspect
import lldb
import optparse
import shlex
import sys
import os
import json

def GetRaincodeSectionAsDict(debugger, result) -> dict:
    """
    Finds the Raincode section and returns the section data as a dictionary.
    """
    target = debugger.GetSelectedTarget()
    n = target.GetNumModules()
    for i in reversed(range(n)):
        mod = target.GetModuleAtIndex(i)
        sec = mod.FindSection("PT_LOAD[1]")
        if not sec:
            continue
        subsec = sec.FindSubSection("Raincode")
        if not subsec:
            continue
        offset = 0
        error = lldb.SBError()
        raincode = subsec.GetSectionData().GetString(error, offset)
        if error.Fail():
            print(error.GetError(), file=result)
            break
        rc = json.loads(raincode)
        return rc
    return {}

class ccsid:
    program = 'ccsid'

    @classmethod
    def register_lldb_command(cls, debugger, module_name):
        parser = cls.create_options()
        cls.__doc__ = parser.format_help()
        # Add any commands contained in this module to LLDB
        command = 'command script add -c %s.%s %s' % (module_name,
                                                      cls.__name__,
                                                      cls.program)
        debugger.HandleCommand(command)
        print('The "{0}" command has been installed, type "help {0}" or "{0} '
              '--help" for detailed help.'.format(cls.program))

    @classmethod
    def create_options(cls):

        usage = "usage: %prog [options]"
        description = ('''CCSID for Raincode/SDM compiled COBOL or PL/I.''');
        # Pass add_help_option = False, since this keeps the command in line
        #  with lldb commands, and we wire up "help command" to work by
        # providing the long & short help methods below.

        # Does optparse have something like:
        # https://docs.python.org/3/library/argparse.html
        #formatter_class=argparse.RawDescriptionHelpFormatter
        parser = optparse.OptionParser(
            description=description,
            prog=cls.program,
            usage=usage,
            add_help_option=False)

        parser.add_option(
            '-s',
            '--set',
            action="store_true",
            dest='set',
            default=False)

        parser.add_option(
            '-h',
            '--help',
            action="store_true",
            dest='help',
            default=False)

        return parser

    def get_short_help(self):
        return "ccsid lookup and set."

    def get_long_help(self):
        return self.help_string

    def __init__(self, debugger, unused):
        self.parser = self.create_options()
        self.debugger = debugger
        self.help_string = self.parser.format_help()

    def __call__(self, debugger, command, exe_ctx, result):
        # Use the Shell Lexer to properly parse up command options just like a
        # shell would
        command_args = shlex.split(command)

        try:
            (options, args) = self.parser.parse_args(command_args)
        except:
            # if you don't handle exceptions, passing an incorrect argument to
            # the OptionParser will cause LLDB to exit (courtesy of OptParse
            # dealing with argument errors by throwing SystemExit)
            result.SetError("option parsing failed")
            return

        # Always get program state from the lldb.SBExecutionContext passed
        # in as exe_ctx
        frame = exe_ctx.GetFrame()
        if not frame.IsValid():
            result.SetError("invalid frame")
            return

        if options.help:
            h = self.get_long_help()
            print( h, file=result )

        if options.set:
            raincode = GetRaincodeSectionAsDict(self.debugger, result)
            try:
                ccsid = raincode['Options']['CCSID']
            except KeyError:
                print("No key CCSID found in raincode section!", file=result)
                return 
            error = debugger.SetInternalVariable("target.charset", f"ibm-{ccsid}", debugger.GetInstanceName())
            if error:
                print(error, file=result)
            else:
                print(f"set target.charset = ibm-{ccsid}", file=result)


def __lldb_init_module(debugger, dict):
    # Register all classes that have a register_lldb_command method
    for _name, cls in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(cls) and callable(getattr(cls,
                                                     "register_lldb_command",
                                                     None)):
            cls.register_lldb_command(debugger, __name__)
