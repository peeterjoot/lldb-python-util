import lldb
import json

# (lldb) command script import xccsid.py
# (lldb) script xccsid.main0()
# target.charset set to ibm-1047
# (lldb) settings show target.charset
# target.charset (string) = "ibm-1047"
#
# or:
#
# (lldb) script xccsid.main()
# (lldb) settings show target.charset
# target.charset (string) = "ibm-1047"

def GetRaincodeSectionAsDict() -> dict:
    """
    Finds the raincode section and returns the section data as a dictionary.
    """
    for i in reversed(range(lldb.target.GetNumModules())):
        mod = lldb.target.GetModuleAtIndex(i)
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
            print(error.GetError())
            break
        return json.loads(raincode)
    return {}

def main0() -> None:
    raincode = GetRaincodeSectionAsDict()
    try:
        ccsid = raincode['Options']['CCSID']
    except KeyError:
        print("No key CCSID found in Raincode section!")
        return 
    result = lldb.SBCommandReturnObject()
    debugger = lldb.target.GetDebugger()
    interpreter = debugger.GetCommandInterpreter()
    command = f"settings set target.charset ibm-{ccsid}"
    interpreter.HandleCommand(command, result)
    if result.Succeeded():
        print(f"target.charset set to ibm-{ccsid}")
        output = result.GetOutput()
        if output:
            print(output)
    else:
        print(f"Error setting target.charset to ibm-{ccsid}")
        error = result.GetError()
        if error:
            print(error)

def main() -> None:
    raincode = GetRaincodeSectionAsDict()
    try:
        ccsid = raincode['Options']['CCSID']
    except KeyError:
        print("No key CCSID found in Raincode section!")
        return 
    debugger = lldb.target.GetDebugger()
    debugger.SetInternalVariable("target.charset", f"ibm-{ccsid}", debugger.GetInstanceName())
