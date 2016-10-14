import pygame
import math
import settingsManager
import spriteManager
import numpy
import copy

def checkGround(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    _object.grounded = False
    _object.ecb.current_ecb.rect.y += 4
    ground_block = pygame.sprite.Group()
    block_hit_list = pygame.sprite.spritecollide(_object.ecb.current_ecb, _objectList, False)
    _object.ecb.current_ecb.rect.y -= 4
    for block in block_hit_list:
        if block.solid or (_object.platform_phase <= 0):
            if _object.ecb.current_ecb.rect.bottom <= block.rect.top+4 and (not _checkVelocity or (hasattr(_object, 'change_y') and hasattr(block, 'change_y') and _object.change_y > block.change_y-1)):
                _object.grounded = True
                ground_block.add(block)
    return ground_block

def checkLeftWall(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    if _object.facing == 1:
        _object.back_walled = False
    else:
        _object.front_walled = False
    _object.ecb.current_ecb.rect.x -= 4
    wall_block = pygame.sprite.Group()
    block_hit_list = pygame.sprite.spritecollide(_object.ecb.current_ecb, _objectList, False)
    _object.ecb.current_ecb.rect.x += 4
    for block in block_hit_list:
        if block.solid:
            if _object.ecb.current_ecb.rect.left >= block.rect.right-4 and (not _checkVelocity or (hasattr(_object, 'change_x') and hasattr(block, 'change_x') and _object.change_x < block.change_x+1)):
                if _object.facing == 1:
                    _object.back_walled = True
                else:
                    _object.front_walled = True
                wall_block.add(block)
    return wall_block

def checkRightWall(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    if _object.facing == 1:
        _object.front_walled = False
    else:
        _object.back_walled = False
    _object.ecb.current_ecb.rect.x += 4
    wall_block = pygame.sprite.Group()
    block_hit_list = pygame.sprite.spritecollide(_object.ecb.current_ecb, _objectList, False)
    _object.ecb.current_ecb.rect.x -= 4
    for block in block_hit_list:
        if block.solid:
            if _object.ecb.current_ecb.rect.right <= block.rect.left+4 and (not _checkVelocity or (hasattr(_object, 'change_x') and hasattr(block, 'change_x') and _object.change_x > block.change_x-1)):
                if _object.facing == 1:
                    _object.front_walled = True
                else:
                    _object.back_walled = True
                wall_block.add(block)
    return wall_block

def checkBackWall(_object, _objectList, _checkVelocity=True):
    if _object.facing == 1:
        _object.checkLeftWall(_object, _objectList, _checkVelocity)
    else:
        _object.checkRightWall(_object, _objectList, _checkVelocity)

def checkFrontWall(_object, _objectList, _checkVelocity=True):
    if _object.facing == 1:
        _object.checkRightWall(_object, _objectList, _checkVelocity)
    else:
        _object.checkLeftWall(_object, _objectList, _checkVelocity)

def checkCeiling(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    _object.ceilinged = False
    _object.ecb.current_ecb.rect.y -= 4
    ceiling_block = pygame.sprite.Group()
    block_hit_list = pygame.sprite.spritecollide(_object.ecb.current_ecb, _objectList, False)
    _object.ecb.current_ecb.rect.y += 4
    for block in block_hit_list:
        if block.solid:
            if _object.ecb.current_ecb.rect.top >= block.rect.bottom-4 and (not _checkVelocity or (hasattr(_object, 'change_y') and hasattr(block, 'change_y') and _object.change_y < block.change_y+1)):
                _object.ceilinged = True
                ceiling_block.add(block)
    return ceiling_block

########################################################

def getMovementCollisionsWith(_object,_spriteGroup):
    future_rect = _object.ecb.current_ecb.rect.copy()
    future_rect.x += _object.change_x
    future_rect.y += _object.change_y
    collide_sprite = spriteManager.RectSprite(_object.ecb.current_ecb.rect.union(future_rect))
    return filter(lambda r: _object.ecb.pathRectIntersects(r.rect, _object.change_x, _object.change_y) <= 1, sorted(pygame.sprite.spritecollide(collide_sprite, _spriteGroup, False), key = lambda q: -_object.ecb.pathRectIntersects(q.rect, _object.change_x, _object.change_y)))

def getSizeCollisionsWith(_object,_spriteGroup):
    return sorted(filter(lambda r: _object.ecb.doesIntersect(r.rect), pygame.sprite.spritecollide(_object.ecb.current_ecb, _spriteGroup, False)), key = lambda q: numpy.linalg.norm(_object.ecb.primaryEjection(q.rect)[0]))

def catchMovement(_object, _other, _platformPhase=False):
    _object.updatePosition(_object.rect)
    _object.ecb.normalize()
    check_rect = _other.rect.copy()
    t = _object.ecb.pathRectIntersects(check_rect, _object.change_x, _object.change_y)

    if _other.solid:
        if not _object.ecb.doesIntersect(check_rect, _dx=t*(_object.change_x), _dy=t*(_object.change_y)):
            return False
        contact = _object.ecb.primaryEjection(check_rect, _dx=t*(_object.change_x), _dy=t*(_object.change_y))
        v_vel = [_object.change_x-_other.change_x, _object.change_y-_other.change_y]
        return numpy.dot(contact[1], v_vel) < 0
    elif not _platformPhase:
        return _object.ecb.interceptPlatform(check_rect, _dx=t*(_object.change_x), _dy=t*(_object.change_y), _yvel=_object.change_y)
    else:
        return False
        
#Prepare for article usage
def eject(_object, _other, _platformPhase=False):
    _object.updatePosition(_object.rect)
    _object.ecb.normalize()
    check_rect = _other.rect.copy()
    
    if _other.solid:
        if _object.ecb.doesIntersect(check_rect):
            contact = _object.ecb.primaryEjection(check_rect)
            _object.rect.x += contact[0][0]
            _object.rect.y += contact[0][1]
            return reflect(_object, _other)
    else:
        if not _platformPhase and _object.ecb.checkPlatform(check_rect, _object.change_y):
            if _object.ecb.doesIntersect(check_rect):
                contact = _object.ecb.primaryEjection(check_rect)
                _object.rect.x += contact[0][0]
                _object.rect.y += contact[0][1]
                return reflect(_object, _other)
    return False

#Prepare for article usage
def reflect(_object, _other):
    if not hasattr(_object, 'elasticity'):
        _object.elasticity = 0
    if not hasattr(_object, 'ground_elasticity'):
        _object.ground_elasticity = 0
    _object.updatePosition(_object.rect)
    _object.ecb.normalize()
    check_rect = _other.rect.copy()

    if _object.ecb.doesIntersect(check_rect):
        contact = _object.ecb.primaryEjection(check_rect)
        #The contact vector is perpendicular to the axis over which the reflection should happen
        v_vel = [_object.change_x-_other.change_x, _object.change_y-_other.change_y]
        if numpy.dot(v_vel, contact[1]) < 0 or True:
            v_norm = [contact[1][1], -contact[1][0]]
            dot = numpy.dot(v_norm, v_vel)
            projection = [v_norm[0]*dot, v_norm[1]*dot] #Projection of v_vel onto v_norm
            elasticity = _object.ground_elasticity if contact[1][1] < 0 else _object.elasticity
            _object.change_x = projection[0]+elasticity*(projection[0]-v_vel[0])+_other.change_x
            _object.change_y = projection[1]+elasticity*(projection[1]-v_vel[1])+_other.change_y
            return True
        else:
            print("Not reflecting!")
    return False

########################################################

def directionalDisplacement(_firstPoints, _secondPoints, _direction):
    #Given a direction to displace in, determine the displacement needed to get it out
    first_dots = numpy.inner(_firstPoints, _direction)
    second_dots = numpy.inner(_secondPoints, _direction)
    projected_displacement = max(second_dots)-min(first_dots)
    norm_sqr = 1.0 if _direction == [0, 0] else _direction[0]*_direction[0]+_direction[1]*_direction[1]
    return [projected_displacement/norm_sqr*_direction[0], projected_displacement/norm_sqr*_direction[1]]

# Returns a 2-entry array representing a range of time when the points and the rect intersect
# If the range's min is greater than its max, it represents an empty interval
#Prepare for article usage
def projectionIntersects(_startPoints, _endPoints, _rectPoints, _vector):
    start_dots = numpy.inner(_startPoints, _vector)
    end_dots = numpy.inner(_endPoints, _vector)
    rect_dots = numpy.inner(_rectPoints, _vector)

    if min(start_dots) == min(end_dots):
        if min(start_dots) <= max(rect_dots): #.O.|...
            t_mins = [float("-inf"), float("inf")]
        else:                               #...|.O.
            t_mins = [float("inf"), float("-inf")]
    elif min(start_dots) > min(end_dots):
        t_mins = [float(max(rect_dots)-min(start_dots))/(min(end_dots)-min(start_dots)), float("inf")]
    else:
        t_mins = [float("-inf"), float(max(rect_dots)-min(start_dots))/(min(end_dots)-min(start_dots))]

    if max(start_dots) == max(end_dots):
        if max(start_dots) >= min(rect_dots): #...|.O.
            t_maxs = [float("-inf"), float("inf")]
        else:                               #.O.|...
            t_maxs = [float("inf"), float("-inf")]
    elif max(start_dots) < max(end_dots):
        t_maxs = [float(min(rect_dots)-max(start_dots))/(max(end_dots)-max(start_dots)), float("inf")]
    else:
        t_maxs = [float("-inf"), float(min(rect_dots)-max(start_dots))/(max(end_dots)-max(start_dots))]

    if max(end_dots)-max(start_dots) == min(end_dots)-min(start_dots):
        if max(start_dots) > min(start_dots):
            t_open = [float("-inf"), float("inf")]
        else:
            t_open = [float("inf"), float("-inf")]
    elif max(end_dots)-max(start_dots) > min(end_dots)-min(start_dots):
        t_open = [float("-inf"), float(max(end_dots)-max(start_dots)-min(end_dots)+min(start_dots))/(max(start_dots)-min(start_dots))]
    else:
        t_open = [float(max(end_dots)-max(start_dots)-min(end_dots)+min(start_dots))/(max(start_dots)-min(start_dots)), float("inf")]

    return [max(t_mins[0], t_maxs[0], t_open[0]), min(t_mins[1], t_maxs[1], t_open[1])]

########################################################
#                       ECB                            #
########################################################        
class ECB():
    def __init__(self,_actor):
        self.actor = _actor

        if hasattr(self.actor, 'sprite'):
            self.current_ecb = spriteManager.RectSprite(self.actor.sprite.bounding_rect.copy(), pygame.Color('#ECB134'))
            self.current_ecb.rect.center = self.actor.sprite.bounding_rect.center
        else:
            self.current_ecb = spriteManager.RectSprite(self.actor.bounding_rect.copy(), pygame.Color('#ECB134'))
            self.current_ecb.rect.center = self.actor.bounding_rect.center
        self.original_size = self.current_ecb.rect.size

        self.previous_ecb = spriteManager.RectSprite(self.current_ecb.rect.copy(), pygame.Color('#EA6F1C'))
        
    """
    Resize the ECB. Give it a height, width, and center point.
    xoff is the offset from the center of the x-bar, where 0 is dead center, negative is left and positive is right
    yoff is the offset from the center of the y-bar, where 0 is dead center, negative is up and positive is down
    """
    def resize(self,_height,_width,_center,_xoff,_yoff):
        pass
    
    """
    Returns the dimensions of the ECB of the previous frame
    """
    def getPreviousECB(self):
        pass
    
    """
    This one moves the ECB without resizing it.
    """
    def move(self,_newCenter):
        self.current_ecb.rect.center = _newCenter
    
    """
    This stores the previous location of the ECB
    """
    def store(self):
        self.previous_ecb = spriteManager.RectSprite(self.current_ecb.rect,pygame.Color('#EA6F1C'))
    
    """
    Set the ECB's height and width to the sprite's, and centers it
    """
    def normalize(self):
        #center = (self.actor.sprite.bounding_rect.centerx + self.actor.current_action.ecb_center[0],self.actor.sprite.bounding_rect.centery + self.actor.current_action.ecb_center[1])
        sizes = self.actor.current_action.ecb_size
        offsets = self.actor.current_action.ecb_offset
        
        
        if sizes[0] == 0: 
            if hasattr(self.actor, 'sprite'):
                self.current_ecb.rect.width = self.actor.sprite.bounding_rect.width
            else:
                self.current_ecb.rect.width = self.actor.bounding_rect.width
        else:
            self.current_ecb.rect.width = sizes[0]
        if sizes[1] == 0: 
            if hasattr(self.actor, 'sprite'):
                self.current_ecb.rect.height = self.actor.sprite.bounding_rect.height
            else:
                self.current_ecb.rect.height = self.actor.bounding_rect.height
        else:
            self.current_ecb.rect.height = sizes[1]
        
        if hasattr(self.actor, 'sprite'):
            self.current_ecb.rect.center = self.actor.sprite.bounding_rect.center
        else:
            self.current_ecb.rect.center = self.actor.bounding_rect.center
        self.current_ecb.rect.x += offsets[0]
        self.current_ecb.rect.y += offsets[1]
        
    def draw(self,_screen,_offset,_scale):
        self.current_ecb.draw(_screen,self.actor.game_state.stageToScreen(self.current_ecb.rect),_scale)
        self.previous_ecb.draw(_screen,self.actor.game_state.stageToScreen(self.previous_ecb.rect),_scale)

    def doesIntersect(self, _other, _dx=0, _dy=0):
        first_points = [[self.current_ecb.rect.centerx+_dx, self.current_ecb.rect.top+_dy], 
                        [self.current_ecb.rect.centerx+_dx, self.current_ecb.rect.bottom+_dy],
                        [self.current_ecb.rect.left+_dx, self.current_ecb.rect.centery+_dy], 
                        [self.current_ecb.rect.right+_dx, self.current_ecb.rect.centery+_dy]]
        second_points = [_other.topleft, _other.topright, _other.bottomleft, _other.bottomright]

        return numpy.dot(directionalDisplacement(first_points, second_points, [float(-1), float(0)]), [float(-1), float(0)]) >= 0 and \
               numpy.dot(directionalDisplacement(first_points, second_points, [float(1), float(0)]), [float(1), float(0)]) >= 0 and \
               numpy.dot(directionalDisplacement(first_points, second_points, [float(0), float(-1)]), [float(0), float(-1)]) >= 0 and \
               numpy.dot(directionalDisplacement(first_points, second_points, [float(0), float(1)]), [float(0), float(1)]) >= 0 and \
               numpy.dot(directionalDisplacement(first_points, second_points, [float(-self.current_ecb.rect.height), float(-self.current_ecb.rect.width)]), [float(-self.current_ecb.rect.height), float(-self.current_ecb.rect.width)]) >= 0 and \
               numpy.dot(directionalDisplacement(first_points, second_points, [float(self.current_ecb.rect.height), float(-self.current_ecb.rect.width)]), [float(self.current_ecb.rect.height), float(-self.current_ecb.rect.width)]) >= 0 and \
               numpy.dot(directionalDisplacement(first_points, second_points, [float(-self.current_ecb.rect.height), float(self.current_ecb.rect.width)]), [float(-self.current_ecb.rect.height), float(self.current_ecb.rect.width)]) >= 0 and \
               numpy.dot(directionalDisplacement(first_points, second_points, [float(self.current_ecb.rect.height), float(self.current_ecb.rect.width)]), [float(self.current_ecb.rect.height), float(self.current_ecb.rect.width)]) >= 0

    def intersectPoint(self, _other, _dx=0, _dy=0):
        first_points = [[self.current_ecb.rect.centerx+_dx, self.current_ecb.rect.top+_dy], 
                        [self.current_ecb.rect.centerx+_dx, self.current_ecb.rect.bottom+_dy],
                        [self.current_ecb.rect.left+_dx, self.current_ecb.rect.centery+_dy], 
                        [self.current_ecb.rect.right+_dx, self.current_ecb.rect.centery+_dy]]
        second_points = [_other.topleft, _other.topright, _other.bottomleft, _other.bottomright]

        norm = numpy.linalg.norm([self.current_ecb.rect.height, self.current_ecb.rect.width])
        if norm == 0:
            norm = 1

        distances = map(lambda k: [directionalDisplacement(first_points, second_points, k), k], [[float(-1), float(0)], [float(1), float(0)], [float(0), float(-1)], [float(0), float(1)], [float(-self.current_ecb.rect.height)/norm, float(-self.current_ecb.rect.width)/norm], [float(self.current_ecb.rect.height)/norm, float(-self.current_ecb.rect.width)/norm], [float(-self.current_ecb.rect.height)/norm, float(self.current_ecb.rect.width)/norm], [float(self.current_ecb.rect.height)/norm, float(self.current_ecb.rect.width)/norm]])
        return min(distances, key=lambda x: x[0][0]*x[1][0]+x[0][1]*x[1][1])

    def ejectionDirections(self, _other, _dx=0, _dy=0):
        first_points = [[self.current_ecb.rect.centerx+_dx, self.current_ecb.rect.top+_dy], 
                        [self.current_ecb.rect.centerx+_dx, self.current_ecb.rect.bottom+_dy],
                        [self.current_ecb.rect.left+_dx, self.current_ecb.rect.centery+_dy], 
                        [self.current_ecb.rect.right+_dx, self.current_ecb.rect.centery+_dy]]
        second_points = [_other.topleft, _other.topright, _other.bottomleft, _other.bottomright]

        norm = numpy.linalg.norm([self.current_ecb.rect.height, self.current_ecb.rect.width])
        if norm == 0:
            norm = 1

        distances = map(lambda k: [directionalDisplacement(first_points, second_points, k), k], [[float(-1), float(0)], [float(1), float(0)], [float(0), float(-1)], [float(0), float(1)], [float(-self.current_ecb.rect.height)/norm, float(-self.current_ecb.rect.width)/norm], [float(self.current_ecb.rect.height)/norm, float(-self.current_ecb.rect.width)/norm], [float(-self.current_ecb.rect.height)/norm, float(self.current_ecb.rect.width)/norm], [float(self.current_ecb.rect.height)/norm, float(self.current_ecb.rect.width)/norm]])

        working_list = filter(lambda e: numpy.dot(e[0], e[1]) >= 0, distances)
        reference_list = copy.deepcopy(working_list)
        for element in reference_list:
            working_list = filter(lambda k: numpy.dot(k[0], element[1]) != numpy.dot(element[0], element[1]) or k[0] == element[0], working_list)
        return working_list

    def primaryEjection(self, _other, _dx=0, _dy=0):
        good_directions = self.ejectionDirections(_other, _dx, _dy)

        first_points = [self.previous_ecb.rect.midtop, self.previous_ecb.rect.midbottom, self.previous_ecb.rect.midleft, self.previous_ecb.rect.midright]
        second_points = [_other.topleft, _other.topright, _other.bottomleft, _other.bottomright]

        norm = numpy.linalg.norm([self.previous_ecb.rect.height, self.previous_ecb.rect.width])
        if norm == 0:
            norm = 1

        distances = map(lambda k: [directionalDisplacement(first_points, second_points, k), k], [[float(-1), float(0)], [float(1), float(0)], [float(0), float(-1)], [float(0), float(1)], [float(-self.previous_ecb.rect.height)/norm, float(-self.previous_ecb.rect.width)/norm], [float(self.previous_ecb.rect.height)/norm, float(-self.previous_ecb.rect.width)/norm], [float(-self.previous_ecb.rect.height)/norm, float(self.previous_ecb.rect.width)/norm], [float(self.previous_ecb.rect.height)/norm, float(self.previous_ecb.rect.width)/norm]])
        previous_dir = min(distances, key=lambda x: x[0][0]*x[1][0]+x[0][1]*x[1][1])
        return min(good_directions, key=lambda y: -numpy.dot(previous_dir[1], y[0])+numpy.linalg.norm(y[0]))
        #return min(good_directions, key=lambda y: numpy.linalg.norm(y[0]))

    def checkPlatform(self, _platform, _yvel):
        first_points = [self.previous_ecb.rect.midtop, self.previous_ecb.rect.midbottom, self.previous_ecb.rect.midleft, self.previous_ecb.rect.midright]
        second_points = [_platform.topleft, _platform.topright, _platform.bottomleft, _platform.bottomright]

        norm = numpy.linalg.norm([self.previous_ecb.rect.height, self.previous_ecb.rect.width])
        if norm == 0:
            norm = 1

        distances = map(lambda k: [directionalDisplacement(first_points, second_points, k), k], [[float(-1), float(0)], [float(1), float(0)], [float(0), float(-1)], [float(0), float(1)], [float(-self.previous_ecb.rect.height)/norm, float(-self.previous_ecb.rect.width)/norm], [float(self.previous_ecb.rect.height)/norm, float(-self.previous_ecb.rect.width)/norm], [float(-self.previous_ecb.rect.height)/norm, float(self.previous_ecb.rect.width)/norm], [float(self.previous_ecb.rect.height)/norm, float(self.previous_ecb.rect.width)/norm]])

        intersect = min(distances, key=lambda x: x[0][0]*x[1][0]+x[0][1]*x[1][1])

        if _platform.top >= self.previous_ecb.rect.bottom-4-_yvel and numpy.dot(intersect[0], intersect[1]) and intersect[1][1] < 0 and self.current_ecb.rect.bottom >= _platform.top:
            return True
        return False

    def interceptPlatform(self, _platform, _dx, _dy, _yvel):
        intersect = self.intersectPoint(_platform, _dx, _dy)
        if _platform.top >= self.current_ecb.rect.bottom-4-_yvel and numpy.dot(intersect[0], intersect[1]) and intersect[1][1] < 0 and self.current_ecb.rect.bottom+_dy >= _platform.top:
            return True
        return False

    def pathRectIntersects(self, _platform, _dx, _dy):
        if self.current_ecb.rect.colliderect(_platform):
            return 0
        start_corners = [self.current_ecb.rect.midtop, self.current_ecb.rect.midbottom, self.current_ecb.rect.midleft, self.current_ecb.rect.midright]
        end_corners = [[self.current_ecb.rect.centerx+_dx, self.current_ecb.rect.top+_dy], 
                       [self.current_ecb.rect.centerx+_dx, self.current_ecb.rect.bottom+_dy],
                       [self.current_ecb.rect.left+_dx, self.current_ecb.rect.centery+_dy], 
                       [self.current_ecb.rect.right+_dx, self.current_ecb.rect.centery+_dy]]
        rect_corners = [_platform.topleft, _platform.topright, _platform.bottomleft, _platform.bottomright]
    
        horizontal_intersects = projectionIntersects(start_corners, end_corners, rect_corners, [1, 0])
        vertical_intersects = projectionIntersects(start_corners, end_corners, rect_corners, [0, 1])
        downward_diagonal_intersects = projectionIntersects(start_corners, end_corners, rect_corners, [self.current_ecb.rect.height, self.current_ecb.rect.width])
        upward_diagonal_intersects = projectionIntersects(start_corners, end_corners, rect_corners, [-self.current_ecb.rect.height, self.current_ecb.rect.width])

        total_intersects = [max(horizontal_intersects[0], vertical_intersects[0], downward_diagonal_intersects[0], upward_diagonal_intersects[0], 0), min(horizontal_intersects[1], vertical_intersects[1], downward_diagonal_intersects[1], upward_diagonal_intersects[1], 1)]
        if total_intersects[0] > total_intersects[1]:
            return 999
        else:
            return total_intersects[0]
