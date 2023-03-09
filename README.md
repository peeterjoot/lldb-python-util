# lldb-python-util

The util.py in this repo adds two lldb commands:

- util
    This has options to cat a file, run a shell, and show the current directory, mirroring functionality available in gdb.
- toggle-assembly
    This is a hacked version of class DisassemblyMode, from https://github.com/llvm/llvm-project/blob/main/lldb/examples/python/disassembly_mode.py (hacked to change the registration method.)

## usage

Add these commands to your lldb session using:

    command script import /path/to/util.py
