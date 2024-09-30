# lldb-python-util

The util.py in this repo adds two lldb commands:

- util.
    This has options to cat a file, run a shell, and show the current directory, mirroring functionality available in gdb.
- toggle-assembly.
    This is a hacked version of class DisassemblyMode, from https://github.com/llvm/llvm-project/blob/main/lldb/examples/python/disassembly_mode.py (hacked to change the registration method, and add a bit more context.)

## usage

Add these commands to your lldb session using:

    command script import /path/to/util.py

# toggle-disassembly help

    (lldb) help toggle-disassembly
    Toggles between a disassembly only mode and normal source mode
    Expects 'raw' input (see 'help raw-input'.)

    Syntax: toggle-disassembly

# util help

    (lldb) help util
    utilities.  Expects 'raw' input (see 'help raw-input'.)

    Syntax: util
    Usage: util [options]

    lldb helper functions.

    Options:
      -p, --pwd             pwd
      -c FILENAME, --cat=FILENAME
                            cat filename
      -s SHELL, --shell=SHELL
                            shell foo
