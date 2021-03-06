from mpf.core.mode import Mode
from numpy import array, zeros, uint8, roll
from numpy.random import randint
from colorsys import hsv_to_rgb


class Bonus10(Mode):
    """ controls the 10 central white playfield cutouts with rad animations """

    def mode_start(self, **kwargs):
        # When the two top targets have been hit, change bumper colors
        self.player.bonus10HitCount = 0
        self.player.bonus10Worth = 1000
        self.add_mode_event_handler('shot_adv_bonus_hit', self.hit)
        self.add_mode_event_handler('bonus10_bonus', self.decrementAniStart)
        self.add_mode_event_handler('roulette_adv_bonus_max', self.hitMax)
        self.bls = [
            getattr(
                self.machine.lights,
                "l_bonus{}".format(i)
            ) for i in range(10)
        ]
        self.cs = zeros(30, dtype=uint8).reshape((3, 10))
        self.colorSet()

    def colorSet(self):
        '''
        set the 10 RGB leds to the values of the `cs` array
        of [3:10] brightness values
        '''
        for i, bl in enumerate(self.bls):
            bl.color(self.cs[:, i].tolist())

    def mode_stop(self, **kwargs):
        self.cs[:] = 0
        self.colorSet()

    def hitMax(self, **kwargs):
        if self.player.bonus10HitCount < 10:
            self.hit()
            # recursively call again in 0.1 seconds
            self.delay.reset(200, self.hitMax, "bonus10AniDelay")

    def hit(self, **kwargs):
        self.player.bonus10HitCount += 1
        hc = self.player.bonus10HitCount
        if hc <= 4:
            cval = 150
        elif hc <= 10:
            # Red and blue channel, 150 --> 0
            # tmp = 150-arange(hc)*ones((3,1))/9*150
            # Green channel, 150 --> 255
            # tmp[1,:] = linspace(150,255,hc)
            # self.cs[:,:hc] = randint(0,4,(3,hc%10))*85
            cval = randint(0, 4, (3, 1)) * 85
        elif hc == 11:
            # Start mega bonus and killer rainbow animation
            self.player.bonus10Worth += 1000
            self.ultraAniStart()
            self.machine.events.post("superMegaHyperBonus")
            return
        else:
            self.machine.events.post("superMegaHyperBonus")
            return
        self.cs[:, :hc] = cval
        self.colorSet()

    def decrementAniStart(self, **kwargs):
        # kwargs = {
        #    'hits': 2,
        #    'score': 2000,
        #    'bonus_score': 2000,
        #    'mode': <Mode.bonus10>
        # }
        self.decrementAni(curLed=min((kwargs["hits"] - 1), 9))

    def decrementAni(self, **kwargs):
        curLed = kwargs["curLed"]
        if curLed >= 0:
            self.cs[:, curLed] = 0
            self.colorSet()
        if curLed > 0:
            curLed -= 1
            # recursively call again in 0.1 seconds
            self.delay.reset(
                200, self.decrementAni, "bonus10AniDelay", curLed=curLed
            )

    def ultraAniStart(self):
        for i in range(10):
            self.cs[:, i] = array(hsv_to_rgb(i / 20, 1, 1)) * 255
        self.ultraAni()

    def ultraAni(self):
        self.cs = roll(self.cs, 1)
        self.colorSet()
        self.delay.reset(100, self.ultraAni, "bonus10AniDelay")
