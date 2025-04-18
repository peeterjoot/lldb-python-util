#!/usr/bin/env python3

# ---------------------------------------------------------------------
# Be sure to add the python path that points to the LLDB shared library.
#
# # To use this in the embedded python interpreter using "lldb" just
# import it with the full path using the "command script import"
# command
#   (lldb) command script import ~/lldb/util.py
# ---------------------------------------------------------------------

from __future__ import print_function

import inspect
import lldb
import optparse
import shlex
import sys
import os


class util:
    program = 'util'

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
        description = ('''lldb helper functions.''');
        #(lldb) util --pwd
        #/home/pjoot/workspace/QA/LzLanguage/Assets/Tests/Raincode/pli/value/value01/0
        #(lldb) util --cat foo
        #/usr/bin/cat: foo: No such file or directory
        #(lldb) util --cat /tmp/q
        #./apis/bswapreloc.py:183:        parser.add_option(
        #...
        #(lldb) util --shell ls
        #JOB11640.RCDP4162.JOBLOG    liblz_pgm_rcdp4162.pds    Makefile    pother.o   RCDP4162.jcl  typescript              value01.o
        #...
        #(lldb) util --shell pwd
        #/home/pjoot/dd
        #(lldb) util --shell /bin/pwd
        #/home/pjoot/workspace/QA/LzLanguage/Assets/Tests/Raincode/pli/value/value01/0

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
            '-p',
            '--pwd',
            action='store_true',
            dest='pwd',
            help='pwd',
            default=False)

        parser.add_option(
            '-c',
            '--cat',
            action='store',
            type='string',
            help='cat filename',
            dest='filename')

        parser.add_option(
            '-s',
            '--shell',
            action='store',
            type='string',
            help='shell foo',
            dest='shell')

        return parser

    def get_short_help(self):
        return "utilities."

    def get_long_help(self):
        return self.help_string

    def __init__(self, debugger, unused):
        self.parser = self.create_options()
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

        if options.pwd:
            p=os.getcwd()
            print(p, file=result)

        if options.filename:
            os.system('/usr/bin/cat %s' % options.filename)

        if options.shell:
            os.system(options.shell)

# variant of: https://github.com/llvm/llvm-project/blob/main/lldb/examples/python/disassembly_mode.py
class DisassemblyMode:
    program = 'toggle-disassembly'

    def __init__(self, debugger, unused):
        self.dbg = debugger
        self.interp = debugger.GetCommandInterpreter()
        self.store_state()
        self.mode_off = True
        
    def store_state(self):
        self.dis_count = self.get_string_value("stop-disassembly-count")
        self.dis_display = self.get_string_value("stop-disassembly-display")
        self.before_count = self.get_string_value("stop-line-count-before")
        self.after_count = self.get_string_value("stop-line-count-after")
        
    def get_string_value(self, setting):
        result = lldb.SBCommandReturnObject()
        self.interp.HandleCommand("settings show " + setting, result)
        value = result.GetOutput().split(" = ")[1].rstrip("\n")
        return value
    
    def set_value(self, setting, value):
        result = lldb.SBCommandReturnObject()
        self.interp.HandleCommand("settings set " + setting + " " + value, result)
        
    def __call__(self, debugger, command, exe_ctx, result):
        if self.mode_off:
            self.mode_off = False
            self.store_state()
            self.set_value("stop-disassembly-display","always")
            self.set_value("stop-disassembly-count", "16")
            self.set_value("stop-line-count-before", "3")
            self.set_value("stop-line-count-after", "0")
            result.AppendMessage("Disassembly mode on.")
        else:
            self.mode_off = True
            self.set_value("stop-disassembly-display",self.dis_display)
            self.set_value("stop-disassembly-count", self.dis_count)
            self.set_value("stop-line-count-before", self.before_count)
            self.set_value("stop-line-count-after", self.after_count)
            result.AppendMessage("Disassembly mode off.")

    def get_short_help(self):
        return "Toggles between a disassembly only mode and normal source mode\n"

    @classmethod
    def register_lldb_command(cls, debugger, module_name):
        #parser = cls.create_options()
        #cls.__doc__ = DisassemblyMode.get_short_help();
        cls.__doc__ = "Toggles between a disassembly only mode and normal source mode\n";
        # Add any commands contained in this module to LLDB
        command = 'command script add -c %s.%s %s' % (module_name,
                                                      cls.__name__,
                                                      cls.program)
        debugger.HandleCommand(command)
        print('The "{0}" command has been installed, type "help {0}" or "{0} '
              '--help" for detailed help.'.format(cls.program))



def __lldb_init_module(debugger, dict):
    # Register all classes that have a register_lldb_command method
    for _name, cls in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(cls) and callable(getattr(cls,
                                                     "register_lldb_command",
                                                     None)):
            cls.register_lldb_command(debugger, __name__)
