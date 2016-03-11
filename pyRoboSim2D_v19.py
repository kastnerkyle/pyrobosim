#!/usr/bin/env python
"""
Simple 2D robot simulator in Python+Pygame (tested in versions 2.6 and 2.7,
under Windows and Ubuntu).

Need to have Python and Pygame (http://www.pygame.org) installed for it to
work. Make sure Python and Pygame versions match, including the number of
bits, e.g. both 32 or both 64.
Launch from its own directory by typing
   python pyrobosim2d_v18.py
in the console/terminal window. May have to add Python dir. to path.

Expects two image files (back2_800_600.bmp, robo2.bmp) in the same directory.

Press ESC to exit, spacebar to teleoperate (arrows for steps in each direction,
'r' to rotate clockwise, 'e' counterclockwise), 'w' to perform a random walk with
random turns when bumping into walls/obstacles, 'a' for autonomous operation
(not implemented, it's the same as W right now), and 't' to toggle the trace
visibility.

The console/terminal window displays the distance (in pixels) and color (4 values:
RGB+transparency alpha) readings of each sensor.


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
--Several "robo" images are provided, with difefrent colors for the robot:
robo1.bmp (gray), robo2.bmp (blue), robo3.bmp (green), robo4.bmp (purple).
Change r_image to the one you like, and remember that this file must be in the
same dir. as the .py file (pyRoboSim_v19.py).
"""

fps                 = 20        #at most  this many frames per second
back_image          = 'back2_800_600.bmp'   #must have this file in same dir.
display_cols        = 800
display_rows        = 600
wall_thickness      = 5         #thickness in pixels
wall_color          = 'black'
food_color          = 'green'
trace_color         = 'blue'
trace_arc           = 10        #in degrees, shows on both sides of r.azi
trace_decrease      = -17       #negative, subtracts from robot size to make a smaller trace
trace_width         = 1
leave_trace         = 0         #default mode is not to leave traces

color_of_nothing    = 'white'
sim_version         = 'RoboSim v.19'

r_image          = 'robo2.bmp'  #must have this file in same dir.
r_edge           = 51       #edge of square surrounding robot (in pixels)
r_init_azi       = 0        #azimuth, in degrees (up is 0)
r_init_x_topleft = 10       #must be >= wall_thickness
r_init_y_topleft = 20
r_step_tele      = 10       #steps for teleop, equal in x or y (in pixels)
r_step_theta     = 7.5      #step for teleop, in azimuth
r_init_fwd_speed = 5        #pixels per simulation cycle
r_init_spin_speed= 3        #degrees per simulation cycle
r_transparency   = 75       #0 is totally transp., 255 totally opaque
r_visual_range   = 200      #measured from robot center
r_visual_angle   = 30       #in degrees, must divide 90 exactly!
r_visual_granularity = 5    #must be < wall_thickness for walls to be detected correctly!


#import everything
import os, pygame
from pygame.locals import *
import math
import random

main_dir = os.path.split(os.path.abspath(__file__))[0]
screen = pygame.display.set_mode((display_cols, display_rows))
list_traces = list()

class Trace():
    def __init__(self, from_rect, start_angle, stop_angle):
        self.rect       = from_rect
        self.start_angle= start_angle
        self.stop_angle = stop_angle

class Obstacle(pygame.Rect):       #for now just colored rectangles
    def __init__(self, x_topleft, y_topleft, width, height, color):
        self.x_topleft  = x_topleft
        self.y_topleft  = y_topleft
        self.width      = width
        self.height     = height
        self.color      = pygame.Color(color)

''' Changes alpha for surfaces with per-pixel alpha; only for small surfaces!
    Sets alpha for WHITE pixels to new_alpha.
    The alpha value is an integer from 0 to 255, 0 is fully transparent and
    255 is fully opaque. '''
def change_alpha_for_white(surface,new_alpha):
    size = surface.get_size()
    if size[0]>300 or size[1]>300:
        print('change_alpha_for_white-> size = ', size, ' IMAGE TOO LARGE!')
        return surface
    for y in range(size[1]):
        for x in range(size[0]):
            r,g,b,a = surface.get_at((x,y))
            if r==255 and g==255 and b==255:
                    surface.set_at((x,y),(r,g,b,new_alpha))
    return surface

''' Changes alpha for surfaces with per-pixel alpha; only for small surfaces!
    Sets alpha for pixels with alpha == 0 to new_alpha. It is needed b/c
    transform.smoothscale pads image with alpha=0. '''
def change_alpha_for_alpha(surface,new_alpha):
    size = surface.get_size()
    for y in range(size[1]):
        for x in range(size[0]):
            r,g,b,a = surface.get_at((x,y))
            if a<200:
                    surface.set_at((x,y),(r,g,b,new_alpha))
    return surface

def draw_traces(target_surf):
    for t in list_traces:
        pygame.draw.arc(target_surf, pygame.Color(trace_color), t.rect,\
                        t.start_angle*math.pi/180, t.stop_angle*math.pi/180, trace_width)

#Create list of obstacles (walls+others)
#First 2 args are x and y of top-left corner, next two width and height, next color
list_obstacles = []
w01 = Obstacle(0,0,display_cols,wall_thickness, wall_color)                          #top wall
list_obstacles.append(w01)
w02 = Obstacle(display_cols-wall_thickness,0,wall_thickness,display_rows,wall_color) #right wall
list_obstacles.append(w02)
w03 = Obstacle(0,display_rows-wall_thickness,display_cols,wall_thickness,wall_color) #bottom wall
list_obstacles.append(w03)
w04 = Obstacle(0,0,wall_thickness,display_rows, wall_color)                          #left wall
list_obstacles.append(w04)
w05 = Obstacle(display_cols/2,display_rows/2,wall_thickness,display_rows/2,wall_color)
list_obstacles.append(w05)
w06 = Obstacle(display_cols/6,display_rows/2,display_rows/4,wall_thickness,wall_color)
list_obstacles.append(w06)

f01 = Obstacle(300,200,20,20,food_color)        #food pellet
list_obstacles.append(f01)

#for collision-checking (right now only in Robot.move()), only the rectangles are needed.
#so for speed a stripped-down list of rectangles is built:
list_rect_obstacles = []
for ob in list_obstacles:
    list_rect_obstacles.append(pygame.Rect(ob.x_topleft,ob.y_topleft,ob.width,ob.height))

class Robot(pygame.sprite.Sprite):
    def __init__(self, image, x_topleft, y_topleft, azimuth, fwd_speed, spin_speed,\
                 visual_range, visual_angle):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        #Sprites must have an image and a rectangle
        self.image          = image
        self.image_original = self.image    #unchanging copy, for rotations
        self.rect           = image.get_rect()
        self.rect_original  = self.rect     #unchanging copy, for rotations
        self.rect.topleft   = x_topleft, y_topleft  #for now used only for initial position
        self.fwd_speed      = fwd_speed
        self.spin_speed     = spin_speed
        self.azi            = azimuth       #in degrees
        self.collided       = False
        self.opmode         = 0             #0=tele, 1=(random)walk 2=auto
        self.spin_angle_left= 0             #relative angle left to spin
        #these are the parameters of the range-sensing system
        self.visual_range   = visual_range
        self.visual_angle   = visual_angle
        self.nr_sensors     = int(2 * 90 / self.visual_angle + 1)
        self.retina         = list([self.visual_range, pygame.Color(color_of_nothing)]\
                                   for i in range(self.nr_sensors))

    def printRetina(self):
        """Prints the content of the retina list"""
        for s in self.retina:
            if (s[0] == self.visual_range): #this really means >=, since sense() func. caps distances
                                            #to visual_range
                print('>'+str(self.visual_range))
            else:       #obstacle detected
                print(s)
        print('\n')

    def update(self):
        """All sprites have an update() method. This function is
        typically called once per frame. IMPORTANT: All actions in
        here execute AFTER the ones called directly in the event loop.
        """
        if   (self.opmode == 0): self.mode_0_tele()     #teleop mode
        elif (self.opmode == 1): self.mode_1_walk()     #RW (random walk)
        elif (self.opmode == 2): self.mode_2_auto()     #autonomous
        else:
            print('ERROR! Undefined operation mode!')

    def mode_0_tele(self):
        #self.sense()       #no sensing here, it's done only at keypress
        if self.collided:
                print('update-->self.opmode==0 THAT HURT!')
                self.collided = False
        #else:                  #teleop mode and not collided
                #do nothing, wait for teleop. commands from kbd.

    def mode_1_walk(self):
        self.sense()
        if self.collided:       #collision in prev. cycle --> start SPIN
                print('update-->self.opmode==1 THAT HURT!')
                self.collided = False
                walk_dazi = random.randint(-180, 180)
                if math.fabs(walk_dazi) <= self.spin_speed:    #can spin in 1 cycle
                    self.spin(walk_dazi)
                else:
                    if walk_dazi > 0:   #calculate the angle's sign
                        sign = 1
                    else:
                        sign = -1
                    self.spin(sign*self.spin_speed)
                    self.spin_angle_left = walk_dazi-sign*self.spin_speed
        else:                   #not collided --> finish SPIN, or MOVE fwd
            if math.fabs(self.spin_angle_left) > 0:     #must finish SPIN
                if math.fabs(self.spin_angle_left) <= self.spin_speed:    #can spin in 1 cycle
                    self.spin(self.spin_angle_left)
                    self.spin_angle_left = 0
                else:
                    if self.spin_angle_left > 0:   #calculate the angle's sign
                        sign = 1
                    else:
                        sign = -1
                    self.spin(sign*self.spin_speed)
                    self.spin_angle_left -= sign*self.spin_speed
            else:                            #MOVE fwd
                #calculate displacements based on azimuth and speed
                temp_unghi = self.azi*math.pi/180
                walk_dx = -self.fwd_speed*math.sin(temp_unghi)
                walk_dy = -self.fwd_speed*math.cos(temp_unghi)
                self.move(walk_dx, walk_dy)
    ########end mode_1_walk(self)########

    def mode_2_auto(self):
        """The Autonomous mode (press key A) is currently an exact copy of the Random Walk mode
        (press key W). This mode is provided simply as a starting point for further changes in the code."""
        self.sense()
        if self.collided:       #collision in prev. cycle --> start SPIN
                print('update-->self.opmode==2 THAT HURT!')
                self.collided = False
                walk_dazi = random.randint(-180, 180)
                if math.fabs(walk_dazi) <= self.spin_speed:    #can spin in 1 cycle
                    self.spin(walk_dazi)
                else:
                    if walk_dazi > 0:   #calculate the angle's sign
                        sign = 1
                    else:
                        sign = -1
                    self.spin(sign*self.spin_speed)
                    self.spin_angle_left = walk_dazi-sign*self.spin_speed
        else:                   #not collided --> finish SPIN, or MOVE fwd
            if math.fabs(self.spin_angle_left) > 0:     #must finish SPIN
                if math.fabs(self.spin_angle_left) <= self.spin_speed:    #can spin in 1 cycle
                    self.spin(self.spin_angle_left)
                    self.spin_angle_left = 0
                else:
                    if self.spin_angle_left > 0:   #calculate the angle's sign
                        sign = 1
                    else:
                        sign = -1
                    self.spin(sign*self.spin_speed)
                    self.spin_angle_left -= sign*self.spin_speed
            else:               #MOVE fwd
                #calculate displacements based on azimuth and speed
                temp_unghi = self.azi*math.pi/180
                walk_dx = -self.fwd_speed*math.sin(temp_unghi)
                walk_dy = -self.fwd_speed*math.cos(temp_unghi)
                self.move(walk_dx, walk_dy)
    ########end mode_2_auto(self)########

    def move(self,dx,dy):
        previous_rect = self.rect           #remember in case undo is necessary
        self.rect = self.rect.move(dx,dy)
        if self.rect.collidelist(list_rect_obstacles) != -1:#if collision exists
            print('mode  -->I collided with wall(s)',\
                  self.rect.collidelistall(list_rect_obstacles))
            self.rect = previous_rect                   #undo the move
            self.collided = True
        else:                   #if there was no collision
            if leave_trace:     #update trace list
                tr = self.rect.inflate(trace_decrease, trace_decrease)
                list_traces.append(Trace(tr, 90+self.azi-trace_arc, 90+self.azi+trace_arc))
    """
    def spin(self,dtheta):
        center = self.rect.center
        self.azi += dtheta
        if self.azi >= 360:         #keep theta between -360..360
            self.azi = self.azi-360
        if self.azi <= -360:
            self.azi = self.azi+360
        temp_rota_imag = pygame.transform.rotate(self.image_original, self.azi)
        self.image = pygame.transform.smoothscale(temp_rota_imag,(r_edge,r_edge))
        #smoothscale pads w/pixels having alpha=0. Increasing alpha to see a faint rect.
        self.image = change_alpha_for_alpha(self.image, r_transparency)
        self.rect = self.image.get_rect()
        self.rect.center = center
        #when using transform.smoothscale, rotations never generate collisions, b/c
        #the image always stays a square of edge r_edge
        if leave_trace:     #update trace list
            tr = self.rect.inflate(trace_decrease, trace_decrease)
            list_traces.append(Trace(tr, 90+self.azi-trace_arc, 90+self.azi+trace_arc))
    """

    def spin(self,dtheta):
        center = self.rect.center
        self.azi += dtheta
        if self.azi >= 360:         #keep theta between -360..360
            self.azi = self.azi-360
        if self.azi <= -360:
            self.azi = self.azi+360
        original_rect = self.image_original.get_rect()
        rotated_image = pygame.transform.rotate(self.image_original, self.azi)
        rotated_rect  = original_rect.copy()
        rotated_rect.center = rotated_image.get_rect().center
        self.image = rotated_image.subsurface(rotated_rect).copy()
        self.image = change_alpha_for_alpha(self.image, r_transparency)
        if leave_trace:     #update trace list
            tr = self.rect.inflate(trace_decrease, trace_decrease)
            list_traces.append(Trace(tr, 90+self.azi-trace_arc, 90+self.azi+trace))

    #this function's job is to place in self.retina the range sensed by each sensor
    def sense(self):
        n = int((self.nr_sensors - 1) // 2)     #the "natural" sensor range is -n to +n
        granu = r_visual_granularity    #must be at least as large as the wall thickness!!
        for i in range(-n, n + 1):         #sense with each of the 2n+1 range sensors
            ang = (self.azi - i*self.visual_angle)*math.pi / 180
            for distance in range(granu, self.visual_range+granu, granu):
                x = self.rect.center[0]-distance*math.sin(ang)  #endpoint coordinates
                y = self.rect.center[1]-distance*math.cos(ang)
                nr_collisions = 0
                count = -1          #needed to coordinate the two lists, to extract color after loop
                for ob in list_rect_obstacles:  #use the stripped-down list of rectangles for speed
                    count = count + 1
                    if ob.collidepoint(x,y):
                        nr_collisions = 1
                        break       #breaks out of wall loop
                if nr_collisions:   #non-zero collision
                    break           #breaks out of distance loop
            #distance now has the min. between the visual range and the first collision
            self.retina[i+n][0] = distance
            if nr_collisions:       #nr_collisions is 1 if a collision has occurred
                self.retina[i+n][1] = list_obstacles[count].color #color comes form the larger list
            else:
                self.retina[i+n][1] = pygame.Color(color_of_nothing)
        #print 'sense -->retina is:\n', self.retina
        self.printRetina()

    def draw_rays(self, target_surf):
        n = int((self.nr_sensors - 1) // 2) #the "natural" sensor range -n to +n
        for i in range(-n,n+1):     #draw the 2n+1 rays of the range sensors
            ang = (self.azi - i*self.visual_angle)*math.pi/180
            x = self.rect.center[0]-self.retina[i+n][0]*math.sin(ang)
            y = self.rect.center[1]-self.retina[i+n][0]*math.cos(ang)
            #use aaline for smoother (but slower) lines
            pygame.draw.line(target_surf, (0,0,0), self.rect.center, (x,y))
########end of Robot class########

def load_image(name):
    path = os.path.join(main_dir, name)
    temp_image = pygame.image.load(path).convert_alpha()  #need this if using ppalpha
    return change_alpha_for_white(temp_image, r_transparency)

###########################################
###########################################
def main():
    global leave_trace, list_traces
    if r_visual_granularity > wall_thickness:
        print('PARAMETER ERROR: r_visual_granularity exceeds wall_thickness!')
        print('This can cause wall detection errors!')
    if r_init_x_topleft<wall_thickness or r_init_y_topleft<wall_thickness:
        print('PARAMETER ERROR: starting position overlaps wall!')
        print('Check r_init_x|y_topleft and wall_thickness')
    pygame.init()           #also calls display.init()
    pygame.display.set_caption(sim_version + ' \tmode: teleoperation')
    r_sprite = load_image(r_image)
    background  = load_image(back_image)

    #prepare simulation objects
    clock = pygame.time.Clock()
    r = Robot(r_sprite, r_init_x_topleft, r_init_y_topleft,r_init_azi, r_init_fwd_speed,\
              r_init_spin_speed, r_visual_range, r_visual_angle)
    allsprites = pygame.sprite.RenderPlain((r))

    #display the environment once, right before event loop
    screen.blit(background, (0, 0))
    count = -1
    for ob in list_obstacles:
        count = count + 1
        s = pygame.display.get_surface()
        s.fill(ob.color, list_rect_obstacles[count])
    r.draw_rays(screen)
    pygame.display.flip()

    going = True
    while going:
        clock.tick(fps)      #at most that many fps

        #Event loop################################
        for event in pygame.event.get():
            if event == QUIT:
                going = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    going = False
                if event.key == K_r:        #r is for rotation
                    r.spin(-r_step_theta)   #clockwise
                    r.sense()       #do it here, to avoid fast scrolling when teleoperating
                if event.key == K_e:        #e is next to r
                    r.spin(r_step_theta)    #counterclockwise
                    r.sense()
                if event.key == K_RIGHT:
                    r.move(r_step_tele,0)
                    r.sense()
                if event.key == K_LEFT:
                    r.move(-r_step_tele,0)
                    r.sense()
                if event.key == K_UP:
                    r.move(0,-r_step_tele)
                    r.sense()
                if event.key == K_DOWN:
                    r.move(0,r_step_tele)
                    r.sense()

                if event.key == K_SPACE:
                    r.opmode = 0            #teleop mode
                    pygame.display.set_caption(sim_version + ' \tmode: teleoperation')
                if event.key == K_w:
                    r.opmode = 1            #random walk mode
                    pygame.display.set_caption(sim_version + ' \tmode: random walk+bounce')
                if event.key == K_a:
                    r.opmode = 2            #autonomous navigation mode
                    pygame.display.set_caption(sim_version + ' \tmode: autonomous')
                if event.key == K_t:        #toggles the tracing mode
                    if leave_trace:
                        leave_trace = 0
                        list_traces = list()
                        print('changing leave_trace from 1 to 0')
                    else:
                        leave_trace = 1
                        print('changing leave_trace from 0 to 1')
        #End of event loop#######################

        #Redrawing
        allsprites.update()
        screen.blit(background, (0, 0))  #redraws the entire bkgrnd.
        #screen.fill((255,255,255)) # white background
        #screen.blit(red_block, (100,100))
        count = -1
        for ob in list_obstacles:
            count = count + 1
            s = pygame.display.get_surface()
            s.fill(ob.color, list_rect_obstacles[count])
        r.draw_rays(screen)
        draw_traces(screen)
        allsprites.draw(screen)


        #pygame.display.update()
        pygame.display.flip()   #all changes are drawn at once (double buffer)
        #pygame.time.delay(100)
    pygame.quit()               #also calls display.quit()


if __name__ == '__main__':
    main()
