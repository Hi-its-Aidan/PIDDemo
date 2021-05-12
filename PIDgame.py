import pygame
import pygame.freetype
import sys

# initialize game
pygame.init()
gainFont = pygame.font.SysFont(None, 25)

# Caption and Icon
pygame.display.set_caption("PID Controller Demo")
icon = pygame.image.load('joystick.png')
pygame.display.set_icon(icon)

# mouse target area
areaRect = pygame.Rect(100, 100, 600, 54)
mouseAreaPNG = pygame.image.load('PIDgradient.png')
mouseAreaPNG = pygame.transform.scale(mouseAreaPNG, (600, 54))
mAreaX = 100
mAreaY = 100


# knob setup
def knobhitbox(cx, cy, r):
    crect = pygame.Rect(cx, cy, r * 2, r * 2)
    return crect


def knobmaker(knob, ang, x, y):
    knob = pygame.transform.rotate(knob, ang)
    new_rect = knob.get_rect(center=knob.get_rect(center=(x, y)).center)
    screen.blit(knob, new_rect)


# initialize variables for the knobs
pknob = pygame.image.load('bcircle.png')
pknob = pygame.transform.scale(pknob, (150, 150))
pAng = 0
iknob = pygame.image.load('rcircle.png')
iknob = pygame.transform.scale(iknob, (150, 150))
iAng = 0
dknob = pygame.image.load('gcircle.png')
dknob = pygame.transform.scale(dknob, (150, 150))
dAng = 0

pRect = knobhitbox(100, 375, 75)
iRect = knobhitbox(325, 375, 75)
dRect = knobhitbox(550, 375, 75)

# follow arrow
arrowFollow = pygame.image.load('left-arrow.png')
arrowFollow = pygame.transform.rotate(arrowFollow, 270)
arrowFollow = pygame.transform.scale(arrowFollow, (25, 25))

arrowX = 375
arrowY = 150

# lead arrow
arrowLead = pygame.image.load('down-arrow.png')
arrowLead = pygame.transform.scale(arrowLead, (25, 25))
leadY = 80
destX = 375

# initialize controller parameters
kp = 5
ki = 2
kd = 0
iError = 0
lastError = 0

# create screen
screen = pygame.display.set_mode((800, 600))


def textBox(text, x, y):
    txt = gainFont.render(text, True, (0, 0, 0), )
    screen.blit(txt, (x, y))


def mousearea(x, y):
    screen.blit(mouseAreaPNG, (x, y))


def followarrow(x, y):
    screen.blit(arrowFollow, (x, y))


def leadarrow(x, y):
    screen.blit(arrowLead, (x, y))


def PIDcontrol(kp, ki, kd, target, current):
    global lastError
    global t0
    global iError

    t1 = pygame.time.get_ticks()
    dt = (t1 - t0)/10
    error = target - current
    iError += (error * dt)
    dError = (error - lastError) / dt

    # account for edge case where changing position causes D gain to spike
    if dError > 500 or dError < -500:
        dError = 0

    gain = kp * error + ki * iError + kd * dError
    t0 = pygame.time.get_ticks()
    lastError = error
    return gain


# initialize click check
clickSet: bool = False

pClick: bool = False

iClick: bool = False

dClick: bool = False

# Game Loop
running: bool = True

t0 = pygame.time.get_ticks()

while running:
    # Screen Background
    screen.fill((255, 204, 102))
    # load images
    mousearea(mAreaX, mAreaY)

    # monitor user interactions
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            running = False
        # Mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Mouse tracking area
            if areaRect.collidepoint(pygame.mouse.get_pos()):
                clickSet = not clickSet
                if clickSet:
                    destX, destY = pygame.mouse.get_pos()
                    destX = destX - 12

            # pKnob Collision detection
            if pRect.collidepoint(pygame.mouse.get_pos()):
                px0, py0 = pygame.mouse.get_pos()
                pClick = not pClick
            # iKnob Collision detection
            if iRect.collidepoint(pygame.mouse.get_pos()):
                ix0, iy0 = pygame.mouse.get_pos()
                iClick = not iClick
            # dKnob Collision detection
            if dRect.collidepoint(pygame.mouse.get_pos()):
                dx0, dy0 = pygame.mouse.get_pos()
                dClick = not dClick

        if event.type == pygame.MOUSEMOTION:
            xdir, ydir = pygame.mouse.get_rel()
            # if the user clicks on a knob, only want the value to increase or decrease
            # based on the direction they drag
            if pClick:
                px1, py1 = pygame.mouse.get_pos()
                if (py0 < py1 and ydir > 0) or (py1 < py0 and ydir < 0):
                    pDelta = round((py0 - py1), 6)
                    pAng = pAng - (pDelta / 4000) * 360
                    if kp + (pDelta / 500) > 10:
                        kp = 10
                    elif kp + (pDelta / 500) < 0:
                        kp = 0
                    else:
                        kp = round(kp + (pDelta / 500), 6)
            if iClick:
                ix1, iy1 = pygame.mouse.get_pos()
                if (iy0 < iy1 and ydir > 0) or (iy1 < iy0 and ydir < 0):
                    iDelta = round((iy0 - iy1), 6)
                    iAng = iAng - (iDelta / 4000) * 360
                    if ki + (iDelta / 500) > 10:
                        ki = 10
                    elif ki + (iDelta / 500) < 0:
                        ki = 0
                    else:
                        ki = round(ki + (iDelta / 500), 6)
            if dClick:
                dx1, dy1 = pygame.mouse.get_pos()
                if (dy0 < dy1 and ydir > 0) or (dy1 < dy0 and ydir < 0):
                    dDelta = round((dy0 - dy1), 6)
                    dAng = dAng - (dDelta / 4000) * 360
                    if kd + (dDelta / 500) > 20:
                        kd = 20
                    elif kd + (dDelta / 500) < 0:
                        kd = 0
                    else:
                        kd = round(kd + (dDelta / 500), 6)

        if event.type == pygame.MOUSEBUTTONUP:
            if pClick:
                pClick = not pClick
            if iClick:
                iClick = not iClick
            if dClick:
                dClick = not dClick

        # if location is set, can flip to opposite side of area with space bar push
        if clickSet:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # mirror over X coordinate 388 (center)
                    if destX > 388:
                        destX = 388 - (destX - 388)
                    elif destX < 388:
                        destX = 388 + (388 - destX)
                    else:
                        pass

    # draw knobs
    textBox(str(kp), 175, 350)
    textBox(str(ki), 400, 350)
    textBox(str(kd), 625, 350)
    knobmaker(pknob, pAng, 175, 450)
    knobmaker(iknob, iAng, 400, 450)
    knobmaker(dknob, dAng, 625, 450)
    textBox("Kp", 170, 440)
    textBox("Ki", 395, 440)
    textBox("Kd", 620, 440)

    # draw the leading arrow
    if not clickSet:
        if areaRect.collidepoint(pygame.mouse.get_pos()):
            destX, destY = pygame.mouse.get_pos()
            destX = destX - 12
            leadarrow(destX, leadY)
    else:
        leadarrow(destX, leadY)

    # draw and move the following arrow
    xmove = PIDcontrol(kp, ki, kd, destX, arrowX)
    xmove = xmove / 500
    arrowX = arrowX + xmove
    followarrow(arrowX, arrowY)
    pygame.time.wait(1)
    pygame.display.update()
