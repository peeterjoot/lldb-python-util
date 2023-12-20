import lldb
import re
import sys

# (lldb) command script import ~/lldb/cobbt.py
# (lldb) script cobbt.main()

# a bunch of this is ripped off from: lldb/packages/Python/lldbsuite/test/lldbutil.py

def get_module_names(thread):
    """
    Returns a sequence of module names from the stack frames of this thread.
    """
    def GetModuleName(i):
        return thread.GetFrameAtIndex(i).GetModule().GetFileSpec().GetFilename()

    return list(map(GetModuleName, list(range(thread.GetNumFrames()))))

def get_function_names(thread):
    """
    Returns a sequence of function names from the stack frames of this thread.
    """
    def GetFuncName(i):
        return thread.GetFrameAtIndex(i).GetFunctionName()

    return list(map(GetFuncName, list(range(thread.GetNumFrames()))))


def get_symbol_names(thread):
    """
    Returns a sequence of symbols for this thread.
    """
    def GetSymbol(i):
        return thread.GetFrameAtIndex(i).GetSymbol().GetName()

    return list(map(GetSymbol, list(range(thread.GetNumFrames()))))

def get_filenames(thread):
    """
    Returns a sequence of file names from the stack frames of this thread.
    """
    def GetFilename(i):
        return thread.GetFrameAtIndex(
            i).GetLineEntry().GetFileSpec().GetFilename()

    return list(map(GetFilename, list(range(thread.GetNumFrames()))))

def get_line_numbers(thread):
    """
    Returns a sequence of line numbers from the stack frames of this thread.
    """
    def GetLineNumber(i):
        return thread.GetFrameAtIndex(i).GetLineEntry().GetLine()

    return list(map(GetLineNumber, list(range(thread.GetNumFrames()))))


def get_pc_addresses(thread):
    """
    Returns a sequence of pc addresses for this thread.
    """
    def GetPCAddress(i):
        return thread.GetFrameAtIndex(i).GetPCAddress()

    return list(map(GetPCAddress, list(range(thread.GetNumFrames()))))


def main() -> None:
    target = lldb.target
    debugger = target.GetDebugger()

    exprOptions = lldb.SBExpressionOptions()
    c = lldb.SBLanguageRuntime_GetLanguageTypeFromString("c")
    exprOptions.SetLanguage( c )

    result = target.EvaluateExpression("(char *)get_perform_stack()", exprOptions)
    
    s = result.GetSummary()
    s = re.sub( r'^"', '', s )
    s = re.sub( r'"$', '', s )
    stack = s.split('\\n')
    n = len(stack) - 1

    thread = lldb.thread
    depth = thread.GetNumFrames()
    mods = get_module_names(thread)
    funcs = get_function_names(thread)
    symbols = get_symbol_names(thread)
    files = get_filenames(thread)
    lines = get_line_numbers(thread)
    addrs = get_pc_addresses(thread)

    skip = {
        "callLoadModule": 1,
        "__clone": 1,
        "DsnCommandProcExec": 1,
        "ewh_call": 1,
        "execute_run_cpu": 1,
        "LAE_execute_linkx": 1,
        "lhe_cpu_thread": 1,
        "lhe_diagnose": 1,
        "lhe_run_cpu": 1,
        "lhe_thread_exit": 1,
        "lz_ikjeft01_batch": 1,
        "lzrexx_main": 1,
        "lzrexx_main_ikjeft01": 1,
        "RDB_LAE_execute_link": 1,
        "start_thread": 1,
        "SubcomHandlerTMP": 1,
        "TmpCommandProcess": 1
    }

    j = 0
    for i in range(depth):
        frame = thread.GetFrameAtIndex(i)
        function = frame.GetFunction()

        load_addr = addrs[i].GetLoadAddress(target)
        if not function:
            file_addr = addrs[i].GetFileAddress()
            start_addr = frame.GetSymbol().GetStartAddress().GetFileAddress()
            symbol_offset = file_addr - start_addr

            s = symbols[i]
            try:
                sk = skip[s]
            except:
                print('  frame #{num}: {addr:#016x} {mod}`{symbol} + {offset}'.format(
                    num=j, addr=load_addr, mod=mods[i], symbol=s, offset=symbol_offset))
                j += 1
        else:
            fn = funcs[i]
            if frame.IsInlined():
                f = '%s [inlined]' % fn
            else:
                f = fn

            if fn.startswith('callLoadModule'):
                sk = 1
            elif fn.startswith('::tso_dsn'):
                sk = 1
            else:
                try:
                    sk = skip[fn]
                except:
                    sk = 0

            if not sk:
                if i==0:
                    print('  frame #{num}: {addr:#016x} {mod}`{func} {symbol} at {file}:{line}'.format(
                        num=j, addr=load_addr, mod=mods[i],
                        func=f,
                        symbol=stack[0],
                        file=files[i], line=lines[i]))
                    j += 1
                    for k in range(1, n-1):
                        print('  frame #{num}: {func} {symbol}'.format(
                            num=j,
                            func=f,
                            symbol=stack[k]))
                        j += 1
                elif i==1:
                    print('  frame #{num}: {addr:#016x} {mod}`{func} {symbol} at {file}:{line}'.format(
                        num=j, addr=load_addr, mod=mods[i],
                        func=f,
                        symbol=stack[n-1],
                        file=files[i], line=lines[i]))
                    j += 1
                else:
                    print('  frame #{num}: {addr:#016x} {mod}`{func} at {file}:{line}'.format(
                        num=j, addr=load_addr, mod=mods[i],
                        func=f,
                        file=files[i], line=lines[i]))
                    j += 1

# vim: et ts=4 sw=4
