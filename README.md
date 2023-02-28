# Lighthouse-Breakout
A [Lighthouse-CAU](https://github.com/ProjectLighthouseCAU) submission in `Wintersemester 22/23` for the module `Einführung in die Informatik` created by Eisiges Eis. It is hardcoded for a screen-size of 28x14 and was not displayed on the high-rise building due to energy saving measurements.

## Quick Start
1. Clone the Repository to your local machine.
2. Place a file named `login.py` in the same folder. Within it, define `username` and `token` accordingly.
3. Start the game through either `python breakout_re.py` or usage of the `controller.ahk` file.

## Playing Guide
### Level Selection
- Press `a` and `d` to select a level with the grey bar.
- Press `w` to confirm your selection.

### In-Game
- Destroy all blocks with the ball to win the round. If your ball hits the bottom, you lose a life. You have a total of 3 lives.
- When the ball is above your grey bar, press `w` to initiate movement.
- Press `a` and `d` to move the grey bar. When the ball is touching the grey bar (dark red indication), you can inflict momentum on the ball by moving the bar.
- Press `s` to pause the game. Then press `w` to resume.

### Block Guide
| Color | Effect |
| --- | --- |
| Red | 1 Strength: destroyed upon hit |
| Green | 2 Strength: Reduced to Red upon hit |
| Blue | 3 Strength: Reduced to Green upon hit |
| Fire | Speeds up Ball and increases maximum speed |
| Ice | Slows down Ball and decreases maximum speed |
| Bomb | Explodes and instantly destroys Blocks within a 4x4 range around the Bomb |
| Grey | Unbreakable Block |

To be implemented: de-buff, buff

### Controller.ahk Controls
I was not able to find a python module which instantly recognizes keys being held down. Controller.ahk is my attempt at a workaround. It provides bulk movement operations as well as options for managing game instances.
- You can configure the controls yourself within controller.ahk.
- You may have to restart controller.ahk (using `ß`) after each window switch for the movement operations `i, j, k, l` to consistently work.

| Key | Usage |
| --- | --- |
| ö | start new game session |
| ä | toggle suspend hotkeys |
| ü | close all open game sessions (active as well as inactive) |
| ß | reload script |
| i | `w` press |
| j | bulk `a` press |
| k | `s` press |
| l | bulk `d` press |

## Ideas for improvement
### Unskippable
- With higher max speed facing illogical physics (prob. something with framecount logic and speed_x being higher than speed_y => frame skipping) and no x movement (x movement being within frames skipped)
- Make fire and ice blocks stable with framecount logic
- Only call wall.update_img() when block collision happened (causes ball trace for some reason, even with value declaration of new img)

### Relevant
- Delete broken items when strength reaches 0
- Add functionality for special blocks
- Add custom block build functionality (x, y, width, height)
- Add more Levels and difficulty setting

### Look-Ahead Collision
- Optimize collision check to only check in range or route of ball

### minor
- Create ball start and reset animations
- ball color turns grey on impact with unbreakable block or high speed (hardly reachable with current speed levels)
- Implement own FPS Clock
- Optimize keybind hold-down recognition <- workaround using autohotkey controller.ahk

## License
[APGL License](LICENSE)
