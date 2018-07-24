class Particle:
    def __init__(self , x , y , vx=0 , vy=0):
        self.pos = PVector(x,y)
        self.ppos = PVector(x-vx , y-vy)
        self.acc = PVector(0 , 0)
        #
        self.radius = 10
        return
    
    def update(self , delta=1):
        self.acc *= delta**2
        pos = ((self.pos * 2) - self.ppos) + self.acc
        self.ppos = self.pos.copy()
        self.pos = pos
        self.acc *= 0
        #
        self.edges()
        return
    
    def collision(self , scene):
        for obj in scene:
            if (self is obj) or (type(obj) == Beam):
                continue
            self.collide(obj)
        self.edges()
        return
    
    def collide(self , other):
        d = self.pos - other.pos
        distance = self.pos.dist(other.pos)
        target = self.radius + other.radius
        ###
        if distance < target:
            resolve = (distance - target) / distance
            d.mult(resolve * 0.5)
            ###
            self.pos -= d
            other.pos += d
            ###
            self.edges()
            other.edges()
        return
    
    def edges(self):
        BOUNCE = 0.8
        vel = self.pos - self.ppos
        ###
        if (self.pos.x - self.radius) < 0:
            self.pos.x = self.radius
            self.ppos.x += vel.x * BOUNCE
            
        elif (self.pos.x + self.radius) > width:
            self.pos.x = width - self.radius
            self.ppos.x += vel.x * BOUNCE
        ###
        if (self.pos.y - self.radius) < 0:
            self.pos.y = self.radius
            self.ppos.y += vel.y * BOUNCE
            
        elif (self.pos.y + self.radius) > height:
            self.pos.y = height - self.radius
            self.ppos.y += vel.y * BOUNCE
        return
    
    def show(self):
        stroke(0)
        strokeWeight(1)
        fill(255)
        ellipse(self.pos.x , self.pos.y , self.radius , self.radius)
        return

class Beam(object):
    def __init__(self , end1 , end2):
        self.end1 = end1
        self.end2 = end2
        #
        self.length = end1.pos.dist(end2.pos)
        self.stiffness = 1.0
        return
    
    def update(self):
        end1 = self.end1
        end2 = self.end2
        overlap = self.length - end1.pos.dist(end2.pos)
        #
        diff = end2.pos - end1.pos
        correct = overlap / self.length
        diff *= correct * 0.5
        diff *= self.stiffness
        #
        end1.pos -= diff
        end2.pos += diff
        return
    
    def show(self):
        strokeWeight(4)
        stroke(255)
        line(self.end1.pos.x , self.end1.pos.y , self.end2.pos.x , self.end2.pos.y)
        return

class Box(object):
    def __init__(self , cx , cy , w=50 , h=50):
        self.points = [Particle(cx-w , cy-h),    #TOP LEFT
                       Particle(cx+w , cy-h),    #TOP RIGHT
                       Particle(cx-w , cy+h),    #BOTTOM LEFT
                       Particle(cx+w , cy+h)]    #BOTTOM RIGHT
        for i in range(len(self.points)):
            print(i , self.points[i].pos)
        #
        self.constraints = [Beam(self.points[0] , self.points[1]),
                            Beam(self.points[1] , self.points[2]),
                            Beam(self.points[2] , self.points[3]),
                            Beam(self.points[3] , self.points[0]),
                            Beam(self.points[0] , self.points[2]),
                            Beam(self.points[1] , self.points[3])]
        for i in range(len(self.constraints)):
            print(i , self.constraints[i].length)
        return
    
    def fall(self , G=1):
        for p in self.points:
            p.acc.y += G/4.0
        return
    
    def collision(self , points):
        for p in self.points:
            p.collision(points)
        return
    
    def update(self , delta):
        for p in self.points:
            p.update(delta)
        #
        for c in self.constraints:
            for _ in range(4):
                c.update()
        return
    
    def show(self):
        for x in self.points + self.constraints:
            x.show()
        #
        cx = 0
        cy = 0
        for p in self.points:
            cx += p.pos.x
            cy += p.pos.y
        cx /= len(self.points)
        cy /= len(self.points)
        strokeWeight(8)
        stroke(255 , 0 , 0)
        point(cx , cy)
        return
