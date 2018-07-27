import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)
import random
from random import randint
import math
import Box2D
from Box2D import (b2AABB, b2GetPointStates, b2QueryCallback, b2Random,  b2Vec2, b2_dynamicBody, b2_kinematicBody)
from Box2D.b2 import (world , polygonShape, staticBody, dynamicBody , kinematicBody)

###

PPM = 13.0
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS
SCREEN_WIDTH, SCREEN_HEIGHT = 1280 , 960
BLANK = (0 , 0 , 0 , 0)
###

blockRotation = 0
blockSize = (1 , 1)
mouseWheel = 0
quakeStep = 0
quakeMag = 1
quakeFreq = 10
quakeVertical = False
quakeActive = False

###

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('GraviTask')
clock = pygame.time.Clock()

world = world(gravity=(0, -10), doSleep=True)

ground_body = world.CreateStaticBody(
    position=(0, 0),
    shapes=(polygonShape(box=(100, 5))),
)

quakeFloor = world.CreateKinematicBody(position=(1 , 6))

quakeFloor.CreateFixture(shape=Box2D.b2PolygonShape(vertices=[(0 , 0),
                                                                      (0 , 1),
                                                                      (40 , 1),
                                                                      (40 , 0)])
                                 ,friction=4)

dynamic_body = world.CreateDynamicBody(position=(10, 15), angle=math.radians(90))

box = dynamic_body.CreatePolygonFixture(box=blockSize, density=1, friction=0.3)

colors = {
    staticBody: (255, 255, 255, 255),
    dynamicBody: (127, 127, 127, 255),
    kinematicBody: (250 , 128 , 0 , 255)
}

maxForces = {}

font = pygame.font.Font(None , 24)
fontLarge = pygame.font.Font(None , 80)

###


icons = {'runningA':pygame.image.load('Textures/Icon_Running_A.png'),
         'runningB':pygame.image.load('Textures/Icon_Running_B.png')}
#
backgrounds = {'sandbox':pygame.image.load('Textures/Background_Sandbox.png')}
#
texture1x1 = pygame.image.load('Textures/RTS_Crate.png')
texture1x2 = pygame.image.load('Textures/RTS_Crate1x2.png')
texture1x4 = pygame.image.load('Textures/RTS_Beam_Grey.png')
texture2x2 = pygame.image.load('Textures/RTS_Crate2x2.png')
textureJoint = pygame.image.load('Textures/RTS_Beam_Red.png')

textures = {
    '1x1':texture1x1,
    (1,1):texture1x1,
    '1x2':texture1x2,
    (2,1):texture1x2,
    '4x0.5':texture1x4,
    (4,0.5):texture1x4,
    '2x2':texture2x2,
    (2,2):texture2x2
    }
###

class Button(object):
    def __init__(self , _pos , _size , _text , _func):
        self.pos = _pos
        self.size = _size
        #
        self.centre = (self.pos[0] + (self.size[0]/2),
                       self.pos[1] + (self.size[1]/2))
        #
        self.text = _text
        self.function = _func
        print(self)
        return

    def pressed(self , mPos):
        if self.pos[0] < mPos[0] < self.pos[0] + self.size[0] and self.pos[1] < mPos[1] < self.pos[1] + self.size[1]:
            # mPos within this AABB
            self.function()
        return

    def draw(self):
        pygame.draw.rect(screen , pygame.Color('White') , (self.pos , self.size) , 0)
        #
        text = fontLarge.render(self.text , True , pygame.Color('Black'))
        pos = (self.centre[0] - (text.get_rect().width/2),
               self.centre[1] - (text.get_rect().height/2))
        #
        screen.blit(text , pos)
        return

class QueryClickCallback(b2QueryCallback):

    def __init__(self, p):
        super(QueryClickCallback, self).__init__()
        self.point = p
        self.fixture = None

    def ReportFixture(self, fixture):
        body = fixture.body
        if body.type == b2_dynamicBody or body.type == b2_kinematicBody:
            inside = fixture.TestPoint(self.point)
            if inside:
                self.fixture = fixture
                # We found the object, so stop the query
                return False
        # Continue the query
        return True

###

def pixelsToWorld(pix):
    pix = [pix[0] , SCREEN_HEIGHT - pix[1]]
    cart = [pix[0]/PPM , pix[1]/PPM]
    return cart

def screenToWorld(pos):
    cart = pixelsToWorld(pos)
    return b2Vec2(cart[0] , cart[1])

def worldToScreen(pos):
    cart = [pos[0] * PPM , SCREEN_HEIGHT - (pos[1] * PPM)]
    return cart

def rectCentre(rect):
    x = (rect[0] + rect[2]) / 2.0
    y = (rect[1] + rect[3]) / 2.0
    return (x , y)

def createBlock(pos):
    global blockRotation
    dynamic_body = world.CreateDynamicBody(position=pos, angle=math.radians(blockRotation))
    block = dynamic_body.CreatePolygonFixture(box=blockSize, density=1, friction=0.3)
    return

def earthQuake(magnitude , vertical=True):
    global quakeStep
    quakeStep += quakeFreq
    if vertical:
        quakeFloor.linearVelocity = (0 , magnitude/2 * math.sin(math.radians(quakeStep)))
    else:
        quakeFloor.linearVelocity = (magnitude * math.sin(math.radians(quakeStep)) , 0)
    return

def displayInfo():
    showBlockRotation(pygame.mouse.get_pos())
    fps = font.render(str(int(clock.get_fps())) , True , pygame.Color('white'))
    infoTxt = "Money: {}".format(money)
    #infoTxt = "Build Phase = {} : QS = {} : QDir = {}".format(not(quakeActive) , quakeStep , 'vertical' if quakeVertical else 'horizontal')
    info = font.render(infoTxt , True , pygame.Color('white'))
    screen.blit(fps , (10 , 10))
    screen.blit(info , (10 , 30))
    return

def showBlockRotation(pos):
    x1 , y1 = pos
    x2 = x1 + math.cos(math.radians(blockRotation)) * 20
    y2 = y1 + math.sin(math.radians(blockRotation)) * 20
    pygame.draw.line(screen , pygame.Color("Green") , pos , (x2 , y2) , 1)
    #
    texture = textures[blockSize]
    scale = ((blockSize[0]*PPM) / texture.get_rect().width) * 2
    img = pygame.transform.rotozoom(texture , blockRotation , scale)
    mPos = pygame.mouse.get_pos()
    pos = (mPos[0] - rectCentre(img.get_rect())[0],
           mPos[1] - rectCentre(img.get_rect())[1])
    screen.blit(img , pos)
    return

###

startButtons = [Button((240 , 200),
                  (800 , 200),
                  'Start',
                  lambda: globals().update({'startMenu':False})),
           Button((240 , 440),
                  (800 , 200),
                  'Options',
                  lambda: globals().update({'optionsMenu':True,
                                            'startMenu':False}))]

x , y = SCREEN_WIDTH , SCREEN_HEIGHT/2
people = [[x+randint(-200 , 1000) , y+randint(0 , y) , bool(randint(0,1)) , 10] for _ in range(5)]

###

money = 100

###

startMenu = True
mainLoop = True
optionsMenu = False
firstBody = None
pause = False
viewTextures = True

###

while mainLoop:
    
    if startMenu:
        
        #############################
        #                           #
        #   START MENU LOOP BELOW   #
        #                           #
        #############################
        
        for event in pygame.event.get():
            if event.type == QUIT:
                startMenu = False
                mainLoop = False
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for button in startButtons:
                    button.pressed(pygame.mouse.get_pos())                # DETERMINE IF EACH BUTTON IS PRESSED OR NOT
        #
        screen.fill((0 , 0 , 128 , 0))
        #
        for person in people:
            img = pygame.transform.scale(icons['runningA' if person[2] else 'runningB'] , (100 , 100))
            screen.blit(img , person[:2])
            person[0] -= randint(8 , 12)
            person[3] -= 1
            if person[3] == 0:
                person[2] = not(person[2])
                person[3] = randint(8 , 12)
            if person[0] < -img.get_rect().width:
                person[0] = SCREEN_WIDTH + randint(100 , 400)
                person[1] = y+randint(0 , y)
        #
        for button in startButtons:
            button.draw()
        #
        pygame.display.update()
        clock.tick(TARGET_FPS)

    elif optionsMenu:

        #############################
        #                           #
        #  OPTIONS MENU LOOP BELOW  #
        #                           #
        #############################


        for event in pygame.event.get():
            if event.type == QUIT:
                mainLoop = False
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for button in buttons:
                    button.pressed(pygame.mouse.get_pos())
        
    else:
        
        #############################
        #                           #
        #   MAIN GAME LOOP BELOW    #
        #                           #
        #############################
        
        for event in pygame.event.get():
            if event.type == QUIT:
                mainLoop = False
            elif (event.type == KEYDOWN and event.key == K_ESCAPE):
                startMenu = True
            elif event.type == pygame.MOUSEBUTTONUP:
                
                #########################
                #                       #
                #   HANDLE MOUSE INPUT  #
                #                       #
                #########################
                
                if event.button == 1 and not(quakeActive):              # CREATE BODY ON LEFT CLICK
                    pos = pixelsToWorld(pygame.mouse.get_pos())
                    createBlock(pos)
                    money -= blockSize[0] * blockSize[1]
                    ###
                elif event.button == 2 and not(quakeActive):            # DELETE BODY ON MIDDLE MOUSE CLICK
                    pos = screenToWorld(pygame.mouse.get_pos())
                    cb = QueryClickCallback(pos)
                    aabb = b2AABB(lowerBound=pos - (0.001 , 0.001),
                                  upperBound=pos + (0.001 , 0.001))
                    world.QueryAABB(cb , aabb)
                    if cb.fixture != None:
                        #money += area(cb.fixture.body)
                        world.DestroyBody(cb.fixture.body)
                    ###
                elif event.button == 3 and not(quakeActive):            # CREATE JOINT ON RIGHT CLICK
                    pos = screenToWorld( pygame.mouse.get_pos())
                    cb = QueryClickCallback(pos)
                    aabb = b2AABB(lowerBound=pos - (0.001, 0.001),
                                  upperBound=pos + (0.001, 0.001))
                    print( aabb )
                    world.QueryAABB( cb, aabb )
                    print( "fixture = ", cb.fixture )
                    if cb.fixture != None:
                        if firstBody == None:
                            firstBody = cb.fixture.body
                            print( "now click on second body\n" )
                        else:
                            if firstBody == cb.fixture.body:
                                print('SAME BODY')
                            else:
                                joint = world.CreateDistanceJoint( bodyA= firstBody, bodyB = cb.fixture.body ,
                                                                   dampingRatio=10.0,
                                                                   frequencyHz=10,
                                                                   collideConnected=True,
                                                                   localAnchorA=firstBody.localCenter,
                                                                   localAnchorB=cb.fixture.body.localCenter,)
                                firstBody = None
                                money -= math.ceil(joint.length)
                    ###
                elif event.button == 4: # SCROLL UP
                    mouseWheel += 1
                    if PPM < 40.0:
                        PPM += 1.0
                    ###
                elif event.button == 5: # SCROOL DOWN
                    mouseWheel -= 1
                    if PPM > 13.0:
                        PPM -= 1.0
                    ###
            elif event.type == pygame.KEYUP:

                #############################
                #                           #
                #   HANDLE KEYBOARDINPUT    #
                #                           #
                #############################
                
                if event.key == pygame.K_q:
                    blockRotation += 15
                elif event.key == pygame.K_e:
                    blockRotation -= 15
                elif event.key == pygame.K_1:
                    blockSize = (1 , 1)
                elif event.key == pygame.K_2:
                    blockSize = (2 , 1)
                elif event.key == pygame.K_3:
                    blockSize = (2 , 2)
                elif event.key == pygame.K_4:
                    blockSize = (4 , 0.5)
                elif event.key == 61: # = KEY
                    quakeMag += 1
                elif event.key == 45: # - KEY
                    quakeMag -= 1
                elif event.key == pygame.K_b:
                    quakeActive = not(quakeActive)
                elif event.key == pygame.K_t:
                    viewTextures = not(viewTextures)
                elif event.key == pygame.K_SPACE:
                    pause = not(pause)
                elif event.key == pygame.K_v:
                    quakeVertical = not(quakeVertical)
                    if quakeActive and quakeVertical:
                        quakeFloor.position = (1 , 6)
                    pass
        #
        screen.fill((0 , 62 , 116))
        #
        if quakeActive:
            earthQuake(quakeMag , quakeVertical)
        else:
            quakeFloor.position = (1 , 5)
            quakeFloor.linearVelocity = (0 , 0)
        #
        for body in world.bodies:
            body.awake = True
            angle = body.angle
            pos = worldToScreen(body.position)
            if body.type == dynamicBody and viewTextures:
                for fixture in body.fixtures:
                    shape = fixture.shape
                    ###
                    if shape.vertices == [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]:
                        texture = textures['1x1']
                    elif shape.vertices == [(-2.0, -1.0), (2.0, -1.0), (2.0, 1.0), (-2.0, 1.0)]:
                        texture = textures['1x2']
                    elif shape.vertices == [(-4.0 , -0.5) , (4.0 , -0.5) , (4.0 , +0.5), (-4.0 , +0.5)]:
                        texture = textures['4x0.5']
                    elif shape.vertices == [(-2.0, -2.0), (2.0, -2.0), (2.0, 2.0), (-2.0, 2.0)]:
                        texture = textures['2x2']
                    else:
                        texture = texture1x2
                    #
                    scale = ((shape.vertices[2][0]*PPM) / texture.get_rect().width) * 2
                    img = pygame.transform.rotozoom(texture , math.degrees(angle) , scale)
                    #
                    sPos = (pos[0] - rectCentre(img.get_rect())[0],
                            pos[1] - rectCentre(img.get_rect())[1])
                    #
                    screen.blit(img , sPos)
                    #
            else:
                for fixture in body.fixtures:
                    shape = fixture.shape
                    #
                    vertices = [(body.transform * v) * PPM for v in shape.vertices]
                    vertices = [(v[0], SCREEN_HEIGHT - v[1]) for v in vertices]
                    #
                    pygame.draw.polygon(screen, colors[body.type], vertices)
        #
        joints = world.joints.copy()
        for joint in joints:
            #
            posA = worldToScreen(joint.bodyA.position)
            posB = worldToScreen(joint.bodyB.position)
            pygame.draw.line(screen , pygame.Color("Red") , posA , posB , 1)
            #
            reactionForce = joint.GetReactionForce(1.0/TIME_STEP)
            totalForce = reactionForce[0]**2 + reactionForce[1]**2
            if totalForce > 10000**2:
                pos = [int((posA[0] + posB[0]) / 2),
                       int((posA[1] + posB[1]) / 2)]
                pygame.draw.circle(screen , pygame.Color("Red") , pos , 100 , 0)
                #
                '''
                joint.bodyA.ApplyForce(force=(1 , 0) , point=joint.anchorA)
                joint.bodyB.ApplyForce(force=(-1 , 0) , point=joint.anchorB)
                '''
                #
                world.DestroyJoint(joint)
        #
        displayInfo()
        if not(quakeActive):
            showBlockRotation(pygame.mouse.get_pos())
        #
        if quakeActive:
            world.Step(TIME_STEP, 10 , 10)
        pygame.display.flip()
        clock.tick(TARGET_FPS)

pygame.quit()
print('Done!')
