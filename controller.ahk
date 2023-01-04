#SingleInstance force
#NoEnv
#IfWinActive ahk_exe firefox.exe
; workaround to the problems faced trying to register key holds
; RunWait, "breakout_re.py"

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

SC027:: ; => ö
    ; Run a game session
    Reload
Return

SC028:: ; => ä
    Suspend, Toggle
Return

SC01A:: ; => ü
    ; Kill all opened cmd sessions
Return

SC00C::Reload ; => ß