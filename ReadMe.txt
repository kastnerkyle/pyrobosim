Simple 2D robot simulator in Python+Pygame (tested in versions 2.6 and 2.7,
under Windows and Ubuntu).

Need to have Python and Pygame (http://www.pygame.org) installed for it to
work. Make sure Python and Pygame versions match, including the number of
bits, e.g. both 32 or both 64.
Launch from its own directory by typing
   python pyrobosim2d_v18.py
in the console/terminal window. May have to add Python dir. to path.

On the Pygame site, as of June 2013, only the 32-bit installers are available for Windows,
so I got the “unofficial” 64-bit installer from 
http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame . 

Expects two image files (back2_800_600.bmp, robo2.bmp) in the same directory.

Press ESC to exit, spacebar to teleoperate (arrows for steps in each direction,
'r' to rotate clockwise, 'e' counterclockwise), 'w' to perform a random walk with
random turns when bumping into walls/obstacles, 'a' for autonomous operation
(not implemented, it's the same as W right now), and 't' to toggle the trace
visibility.

The console/terminal window displays the distance (in pixels) and color (4 values:
RGB+transparency alpha) readings of each sensor.

The Autonomous mode (press key A) is currently an exact copy of the Random Walk mode
(press key W). This mode is implemented in method mode_2_auto() of the Robot class, and
is provided simply as a starting point for further changes in the code.

Send your questions to agapie@tarleton.edu



    Copyright (C) 2013 Mircea Agapie 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.



Changes in version 19:
--Sensor data is written in the console window only for those sensors that are
seeing something; the others only display "> range"
--When spinning, the size of the robot image does not change anymore