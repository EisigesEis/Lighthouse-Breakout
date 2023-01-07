#SingleInstance force
#NoEnv
; workaround to the problems faced trying to register key holds

;list of inputs:
; ö => start new game session, reload script
; ä => suspend hotkeys
; ü => close all open game sessions (active as well as in-active)
; ß => reload script (recommended after window switching)
; RESTART (press ß) AFTER EACH WINDOW SWITCH FOR THE FOLLOWING TO CONSISTENTLY WORK:
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
    MsgBox, 4356, Breakout Controller, Confirm attempt to close ALL active game sessions?
    IfMsgBox Yes
    {
        if sessionPIDs.MaxIndex() {
            For k, v in sessionPIDs {
                WinClose, ahk_pid %PID%
            }
            sessionPIDs := []
        } else {
            MsgBox, 4356, Breakout Controller, No active sessions saved.`nClose all cmd.exe processes? ; 4+256+4096
            IfMsgBox Yes
            { ; close cmd logic from yeeswg - https://www.autohotkey.com/boards/viewtopic.php?t=38139
                WinGet, vWinList, List, ahk_class ConsoleWindowClass
                Loop, % vWinList
                {
                    hWnd := vWinList%A_Index%
                    WinGetTitle, vWinTitle, % "ahk_id " hWnd
                    MsgBox, 3,, "Close the following? `r`n" %vWinTitle%
                    IfMsgBox, Yes
                        WinClose, % "ahk_id " hWnd
                }
            }
        }
    }
Return

SC00C::Reload ; => ß


; #IfWinActive ahk_exe firefox.exe
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