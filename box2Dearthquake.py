import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)
import random
import math
import Box2D
from Box2D import (b2AABB, b2GetPointStates, b2QueryCallback, b2Random,  b2Vec2, b2_dynamicBody, b2_kinematicBody)
from Box2D.b2 import (world , polygonShape, staticBody, dynamicBody , kinematicBody)

###

PPM = 13.0
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS
SCREEN_WIDTH, SCREEN_HEIGHT = 1280 , 960
###

blockRotation = 0
blockSize = (1 , 1)
mouseWheel = 0
quakeStep = 0
quakeMag = 1
quakeVertical = False
quakeActive = False

###

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('GraviTask')
clock = pygame.time.Clock()

world = world(gravity=(0, -10), doSleep=True)

ground_shape = Box2D.b2PolygonShape(vertices = [(0 , 10),
                                                (2 , 1),
                                                (98 , 1),
                                                (100 , 10),
                                                (100 , 0),
                                                (0 , 0)])

ground_body = world.CreateStaticBody(
    position=(0, 0),
    shapes=ground_shape#polygonShape(box=(100, 5)),
)

quakeFloor = world.CreateKinematicBody(position=(1 , 6))

quakeFloor.CreateFixture(shape=Box2D.b2PolygonShape(vertices=[(0 , 0),
                                                                      (0 , 1),
                                                                      (40 , 1),
                                                                      (40 , 0)])
                                 ,friction=4)

dynamic_body = world.CreateDynamicBody(position=(10, 15), angle=math.radians(90))

box = dynamic_body.CreatePolygonFixture(box=blockSize, density=1, friction=0.3)
print(box.shape.vertices)
colors = {
    staticBody: (255, 255, 255, 255),
    dynamicBody: (127, 127, 127, 255),
    kinematicBody: (250 , 128 , 0 , 255)
}

maxForces = {}

font = pygame.font.Font(None , 30)

###

texture1x1 = pygame.image.load('RTS_Crate.png')
texture1x2 = pygame.image.load('RTS_Crate1x2.png')
texture1x4 = pygame.image.load('RTS_Beam2x05.png')
texture2x2 = pygame.image.load('RTS_Crate2x2.png')

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
    print(block.shape.vertices)
    return

def earthQuake(magnitude , vertical=True):
    global quakeStep
    quakeStep += 8
    if vertical:
        quakeFloor.linearVelocity = (0 , magnitude * math.sin(math.radians(quakeStep)))
    else:
        quakeFloor.linearVelocity = (magnitude * math.sin(math.radians(quakeStep)) , 0)
    return

def displayInfo():
    showBlockRotation(pygame.mouse.get_pos())
    fps = font.render(str(int(clock.get_fps())) , True , pygame.Color('white'))
    infoTxt = "Build Phase = {} : QS = {} : QDir = {}".format(not(quakeActive) , quakeStep , 'vertical' if quakeVertical else 'horizontal')
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
    img = pygame.transform.rotozoom(texture , blockRotation , blockSize[1]/PPM)
    mPos = pygame.mouse.get_pos()
    pos = (mPos[0] - rectCentre(img.get_rect())[0],
           mPos[1] - rectCentre(img.get_rect())[1])
    screen.blit(img , pos)
    return

###
firstBody = None
running = True
pause = False
viewTextures = False
while running:
    ###
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and not(quakeActive):
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
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
                else:
                    pos = pixelsToWorld(pygame.mouse.get_pos())
                    createBlock(pos)
            elif event.button == 4: # SCROLL UP
                mouseWheel += 1
                if PPM < 100.0:
                    PPM += 1.0
            elif event.button == 5: # SCROOL DOWN
                mouseWheel -= 1
                if PPM > 13.0:
                    PPM -= 1.0
        elif event.type == pygame.KEYUP:
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
    screen.fill((0, 0, 0, 0))
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
        for fixture in body.fixtures:
            shape = fixture.shape
            ###
            if viewTextures:
                if shape.vertices == [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]:
                    texture = textures['1x1']
                elif shape.vertices == [(-2.0, -1.0), (2.0, -1.0), (2.0, 1.0), (-2.0, 1.0)]:
                    texture = textures['1x2']
                elif shape.vertices == [(-2.0, -2.0), (2.0, -2.0), (2.0, 2.0), (-2.0, 2.0)]:
                    texture = textures['2x2']
                else:
                    texture = texture1x2
                #
                img = pygame.transform.rotozoom(texture , math.degrees(angle) , 0.1)
                #
                sPos = (pos[0] - rectCentre(img.get_rect())[0],
                        pos[1] - rectCentre(img.get_rect())[1])
                #
                screen.blit(img , sPos)
            else:
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
        totalForce = math.sqrt( reactionForce[0] * reactionForce[0] + reactionForce[1] * reactionForce[1] )
        if totalForce > 10000:
            pos = [int((posA[0] + posB[0]) / 2),
                   int((posA[1] + posB[1]) / 2)]
            pygame.draw.circle(screen , pygame.Color("Red") , pos , 100 , 0)
            world.DestroyJoint( joint )
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
