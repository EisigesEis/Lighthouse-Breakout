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

SC01A:: ; => ü
    ; Kill all open game sessions
    For k, v in sessionPIDs {
        WinActivate, ahk_pid %v%
        Sleep 40
        Send ^{c}
        ; ControlSend,, ^{c}, ahk_pid %v% ; inconsistent
        Process, Close, %v%
    }
    sessionPIDs := []
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