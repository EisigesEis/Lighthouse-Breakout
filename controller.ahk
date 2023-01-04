#SingleInstance force
#NoEnv
; workaround to the problems faced trying to register key holds

;list of inputs:
; ö => start new game session, reload script
; ä => suspend hotkeys
; ü => close all open game sessions (active as well as in-active)
; ß => reload script (recommended after window switching)
;
; i => up press (w)
; j => bulk left movement (a)
; k => down press (s)
; l => bulk right movement (d)

sessionPIDs := []
SC027:: ; => ö
    ; Start a game session
    Run, %ComSpec% /K python breakout_re.py,,,PID

    sessionPIDs.Push(PID) ; add game session PID for closing later
Return

SC028:: ; => ä
    Suspend, Toggle
Return

disassembleCMD(PID)
{
    WinActivate, ahk_pid %PID%
    Sleep 40
    ; Send ^{c}
    ; Sleep 40
    ; ControlSend,, !{F4}, ahk_pid %v% ; inconsistent
    ; Process, Close, %PID% ; inconsistent
    ; WinClose, ahk_pid %PID% ; inconsistent?
    Send !{F4}
}

SC01A:: ; => ü
    ; Kill all open game sessions
    if sessionPIDs.MaxIndex() {
        For k, v in sessionPIDs {
            disassembleCMD(v)
        }
        sessionPIDs := []
    } else {
        MsgBox, 4372, Breakout Controller, No active sessions saved.`nClose all cmd.exe processes? ; 4+16+256+4096
        IfMsgBox Yes
            while WinExist(ahk_exe cmd.exe)
                WinGet, v, PID, ahk_exe cmd.exe
                disassembleCMD(v)
    }
Return

SC00C::Reload ; => ß


#IfWinActive ahk_exe firefox.exe
j::
    while GetKeyState("j","P")
    {
        Send {a}
        sleep 1
    }
Return

l::
    while GetKeyState("l","P")
    {
        Send {d}
        Sleep 1
    }
Return

i::
    Send {w}
Return

k::
    Send {s}
Return