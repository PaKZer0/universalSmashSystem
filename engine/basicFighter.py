import settingsManager
import vector2D

class BasicFighter():
    def __init__(self,
                 playerNum,
                 sprite,
                 attributes):
        
        self.attr = attributes
        self.vars = {}
        self.flags = {}
        self.functionHooks = {
                              'beforeUpdate': [],
                              'afterUpdate' : []
                              }
        
        self.sprite = sprite
        self.current_action = None
        
        self.velocity = vector2D.Vec2d()
        self.actions = settingsManager.importFromURI(__file__,'baseActions.py')
        
    def update(self):
        for func in self.functionHooks['beforeUpdate']:
            func(self)
            
        for func in self.functionHooks['afterUpdate']:
            func(self)
########################################################
#                  ACTION SETTERS                      #
########################################################
    
    """
    These functions are meant to be overridden. They are
    provided so the baseActions can change the AbstractFighter's
    actions. If you've changed any of the base actions
    for the fighter (including adding a sprite change)
    override the corresponding method and have it set
    an instance of your overridden action.
    """

    def changeAction(self,newAction):
        newAction.setUp(self,self.current_action)
        self.current_action.tearDown(self,newAction)
        self.current_action = newAction
        
    def doIdle(self):
        self.changeAction(self.actions.NeutralAction())

    def doCrouch(self):
        self.changeAction(self.actions.Crouch())

    def doCrouchGetup(self):
        self.changeAction(self.actions.CrouchGetup())
        
    def doGroundMove(self,direction):
        self.changeAction(self.actions.Move())

    def doDash(self,direction):
        self.changeAction(self.actions.Dash())

    def doRun(self,direction):
        self.changeAction(self.actions.Run())

    def doHitStun(self,hitstun,trajectory, hitstop):
        self.changeAction(self.actions.HitStun(hitstun,trajectory, hitstop))

    def doTryTech(self, hitstun, trajectory, hitstop):
        self.changeAction(self.actions.TryTech(hitstun, trajectory, hitstop))
    
    def doPivot(self):
        self.changeAction(self.actions.Pivot())
    
    def doStop(self):
        self.changeAction(self.actions.NeutralAction())

    def doRunPivot(self):
        self.changeAction(self.actions.RunPivot())

    def doRunStop(self):
        self.changeAction(self.actions.RunStop())
    
    def doLand(self):
        self.changeAction(self.actions.Land())

    def doHelplessLand(self):
        self.changeAction(self.actions.HelplessLand())
    
    def doFall(self):
        self.changeAction(self.actions.Fall())

    def doHelpess(self):
        self.changeAction(self.actions.Helpless())

    def doJump(self):
        self.changeAction(self.actions.Jump())
        
    def doGroundJump(self):
        self.changeAction(self.actions.Jump())
    
    def doAirJump(self):
        self.changeAction(self.actions.AirJump())

    def doTrip(self, length, direction):
        self.changeAction(self.actions.Trip(length, direction))

    def doGetup(self, direction):
        self.changeAction(self.actions.Getup(direction))
    
    def doGroundAttack(self):
        return None

    def doDashAttack(self):
        return None
    
    def doAirAttack(self):
        return None

    def doGetupAttack(self, direction):
        return None

    def doGroundGrab(self):
        return None

    def doAirGrab(self):
        return None

    def doTrapped(self, length):
        self.changeAction(self.actions.Trapped(length))

    def doStunned(self, length):
        self.changeAction(self.actions.Stunned(length))

    def doGrabbed(self,height):
        self.changeAction(self.actions.Grabbed(height))

    def doRelease(self):
        self.changeAction(self.actions.Release())

    def doReleased(self):
        self.changeAction(self.actions.Released())

    def doGrabbing(self):
        self.changeAction(self.actions.Grabbing())

    def doPummel(self):
        return None

    def doThrow(self):
        return None

    def doPreShield(self):
        self.changeAction(self.actions.PreShield())
   
    def doShield(self):
        self.changeAction(self.actions.Shield())

    def doShieldStun(self, length):
        self.changeAction(self.actions.ShieldStun(length))
        
    def doForwardRoll(self):
        self.changeAction(self.actions.ForwardRoll())
    
    def doBackwardRoll(self):
        self.changeAction(self.actions.BackwardRoll())
        
    def doSpotDodge(self):
        self.changeAction(self.actions.SpotDodge())
        
    def doAirDodge(self):
        self.changeAction(self.actions.AirDodge())

    def doTechDodge(self):
        self.changeAction(self.actions.TechDodge())
        
    def doLedgeGrab(self,ledge):
        self.changeAction(self.actions.LedgeGrab(ledge))
        
    def doLedgeGetup(self):
        self.changeAction(self.actions.LedgeGetup())

    def doLedgeAttack(self):
        self.changeAction(self.actions.LedgeAttack())

    def doLedgeRoll(self):
        self.changeAction(self.actions.LedgeRoll())
        
    def doGetTrumped(self):
        print("trumped")
        
########################################################
#                  STATE CHANGERS                      #
########################################################
    

########################################################
#                 ENGINE FUNCTIONS                     #
########################################################
    
    def registerFunction(self,hook,func):
        self.functionHooks[hook].append(func)
        
    def unregisterFunction(self,hook,func):
        self.functionHooks[hook].remove(func)
    
