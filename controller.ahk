#SingleInstance force
#NoEnv
#IfWinActive ahk_exe firefox.exe
; A cheap workaround to the problems faced trying to register key holds
; RunWait, "breakout_re.py"

$Left::
    while GetKeyState("Left","P")
    {
        Send {a}
        sleep 1
    }
Return

$Right::
    while GetKeyState("Right","P")
    {
        Send {d}
        Sleep 1
    }
Return

$Up::
    Send {w}
Return

$Down::
    Send {s}
Return

; ~RShift::suspend
; ~LCtrl::Reload