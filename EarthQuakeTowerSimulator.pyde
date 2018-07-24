from Physics import *

def setup():
    size(800,600)
    frameRate(60)
    #
    ellipseMode(RADIUS)
    #
    '''
    for _ in range(32):
        p = Particle(random(width) , random(height) , random(-1,1) , random(-1,1))
        points.append(p)
    #
    global beams
    beams = [Beam(points[0] , points[1]),
             Beam(points[1] , points[2]),
             Beam(points[2] , points[3]),
             Beam(points[3] , points[0]),
             Beam(points[1] , points[3])]
    '''
    return

points = []
beams = []
boxes = []
testBox = Box(400 , 300)
boxes.append(testBox)

def draw():
    background(51)
    #
    iterations = 8
    delta = 1.0 / iterations
    '''
    for _ in range(iterations):
        for p in points:
            p.acc.y += 0.1
            p.update(delta)
            p.collision(points)
        
        for b in beams:
            b.update()
    #
    for obj in points + beams:
        obj.show()
    
    for i in range(len(testBox.points)):
        testBox.points[i].acc.y += 0.5
    #
    for _ in range(iterations):
        testBox.update(delta)
    #
    testBox.show()
    '''
    for b in boxes:
        b.fall()
        for _ in range(iterations):
            b.update(delta)
            b.collision(points)
        b.show()
    return

def mousePressed():
    boxes.append(Box(mouseX , mouseY))
    return
