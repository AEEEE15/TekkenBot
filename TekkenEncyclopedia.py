"""
Collects information from TekkenGameState over time in hopes of synthesizing it and presenting it in a more useful way.

"""

from MoveInfoEnums import AttackType
from TekkenGameState import TekkenGameState
import sys


class TekkenEncyclopedia:
    def __init__(self, isPlayerOne = False, print_extended_frame_data = False):
        self.FrameData = {}
        self.isPlayerOne = isPlayerOne
        self.print_extended_frame_data = print_extended_frame_data

        self.active_frame_wait = 1
        self.second_opinion = False
        self.second_opinion_timer = 0
        self.stored_prefix = ""
        self.stored_opp_id = 0
        self.stored_opp_recovery = 0
        self.stored_bot_recovery = 0




    def GetFrameAdvantage(self, moveId, isOnBlock = True):
        if moveId in self.FrameData:
            if isOnBlock:
                return self.FrameData[moveId].onBlock
            else:
                return self.FrameData[moveId].onNormalHit
        else:
            return None


    #Set the dummy to jump and hold up and this prints the frame difference.
    def CheckJumpFrameDataFallback(self, gameState):
        if not self.isPlayerOne:
            if gameState.IsFulfillJumpFallbackConditions():
                print("p1 jump frame diff: " + str(gameState.GetBotMoveTimer() - gameState.GetOppMoveTimer()))

    def Update(self, gameState: TekkenGameState):
        if self.isPlayerOne:
            gameState.FlipMirror()
            #gameState.stateLog[-1].opp.PrintYInfo()
            #print(gameState.GetOppTechnicalStates())
            #print(gameState.stateLog[-1].opp.simple_state)
            #print(gameState.stateLog[-1].opp.complex_state)


            if len(gameState.stateLog) > 2:
                if gameState.stateLog[-1].bot.complex_state != gameState.stateLog[-2].bot.complex_state:
                    pass
                    #print(gameState.stateLog[-1].bot.complex_state)
                if gameState.stateLog[-1].opp.simple_state != gameState.stateLog[-2].opp.simple_state:
                    #print(gameState.stateLog[-1].opp.simple_state)
                    pass
                if gameState.stateLog[-1].opp.move_id != gameState.stateLog[-2].opp.move_id:
                    #print(gameState.stateLog[-1].opp.move_id)
                    pass
                if gameState.stateLog[-1].opp.stun_state != gameState.stateLog[-2].opp.stun_state:
                    pass
                    #print(gameState.stateLog[-1].opp.stun_state)
                if gameState.stateLog[-1].bot.stun_state != gameState.stateLog[-2].bot.stun_state:
                    pass
                    #print(gameState.stateLog[-1].bot.stun_state)
                if gameState.stateLog[-1].opp.mystery_state != gameState.stateLog[-2].opp.mystery_state:
                    pass
                    #print(gameState.stateLog[-1].opp.mystery_state)
                    #print('b{}'.format(gameState.stateLog[-1].bot.mystery_state))
                if gameState.stateLog[-1].bot.mystery_state != gameState.stateLog[-2].bot.mystery_state:
                    pass
                    #print('{}'.format(gameState.stateLog[-1].bot.mystery_state))
                if gameState.stateLog[-1].bot.hit_outcome != gameState.stateLog[-2].bot.hit_outcome:
                    pass
                    #print(gameState.stateLog[-1].bot.hit_outcome)





        #self.CheckJumpFrameDataFallback(gameState)

        opp_id = gameState.GetOppMoveId()

        if self.second_opinion:
            self.second_opinion_timer += 1
            landingCanceledFrames = gameState.GetOppMoveInterruptedFrames()
            if landingCanceledFrames > 0:
                bot_recovery = (gameState.GetBotRecovery() - gameState.GetBotMoveTimer())
                opp_recovery = (gameState.GetOppRecovery() - gameState.GetOppMoveTimer())
                #fa = (self.stored_bot_recovery - self.second_opinion_timer) - opp_recovery
                if self.second_opinion_timer < self.stored_bot_recovery:
                    fa = bot_recovery - opp_recovery
                else:
                    fa = (self.stored_bot_recovery - self.second_opinion_timer) - opp_recovery
                fa_string = self.FrameData[self.stored_opp_id].WithPlusIfNeeded(fa)

                print(self.stored_prefix + "JUMP CANCELED -> " + fa_string + " NOW:" + fa_string)

                self.second_opinion = False
                self.second_opinion_timer = 0

            if self.second_opinion_timer > self.stored_opp_recovery:
                #print("check {}".format(self.stored_opp_recovery))
                #print(gameState.stateLog[-1].opp.IsBufferable())
                #print(gameState.GetOppTechnicalStates(self.stored_opp_recovery)[2])
                #print(gameState.GetOppTechnicalStates(self.stored_opp_recovery)[3])
                self.second_opinion = False
                self.second_opinion_timer = 0


        if (gameState.IsOppWhiffingXFramesAgo(self.active_frame_wait + 1)) and \
                (gameState.IsBotBlocking()  or gameState.IsBotGettingHit() or gameState.IsBotBeingThrown() or gameState.IsBotStartedBeingJuggled() or gameState.IsBotBeingKnockedDown() or gameState.IsBotJustGrounded()):

            if gameState.DidBotIdChangeXMovesAgo(self.active_frame_wait)  or gameState.DidBotTimerReduceXMovesAgo(self.active_frame_wait): #or gameState.DidOppIdChangeXMovesAgo(self.active_frame_wait):
                gameState.BackToTheFuture(self.active_frame_wait)

                if not self.active_frame_wait >= gameState.GetOppActiveFrames() + 1:
                    self.active_frame_wait += 1
                else:
                    gameState.ReturnToPresent()

                    if opp_id in self.FrameData:
                        frameDataEntry = self.FrameData[opp_id]
                    else:
                        frameDataEntry = FrameDataEntry(self.print_extended_frame_data)
                        self.FrameData[opp_id] = frameDataEntry

                    frameDataEntry.currentActiveFrame = gameState.GetLastActiveFrameHitWasOn(self.active_frame_wait)

                    gameState.BackToTheFuture(self.active_frame_wait)

                    frameDataEntry.currentFrameAdvantage = '??'
                    frameDataEntry.move_id = opp_id
                    #frameDataEntry.damage =
                    frameDataEntry.damage = gameState.GetOppDamage()
                    frameDataEntry.startup = gameState.GetOppStartup()

                    if frameDataEntry.damage == 0 and frameDataEntry.startup == 0:
                        frameDataEntry.startup, frameDataEntry.damage = gameState.GetOppLatestNonZeroStartupAndDamage()

                    frameDataEntry.activeFrames = gameState.GetOppActiveFrames()
                    frameDataEntry.hitType = AttackType(gameState.GetOppAttackType()).name
                    if gameState.IsOppAttackThrow():
                        frameDataEntry.hitType += "_THROW"

                    fastestRageMoveFrames = 120
                    longestRageMoveFrames = 150
                    if frameDataEntry.startup > fastestRageMoveFrames: #and gameState.DidOpponentUseRageRecently(longestRageMoveFrames):
                        frameDataEntry.startup = gameState.GetBotElapsedFramesOfRageMove(frameDataEntry.startup)

                    frameDataEntry.recovery = gameState.GetOppRecovery()

                    frameDataEntry.input = frameDataEntry.InputTupleToInputString(gameState.GetOppLastMoveInput())



                    frameDataEntry.technical_state_reports = gameState.GetOppTechnicalStates(frameDataEntry.startup)

                    gameState.ReturnToPresent()


                    time_till_recovery_opp = gameState.GetOppRecovery() - gameState.GetOppMoveTimer()
                    time_till_recovery_bot = gameState.GetBotRecovery() - gameState.GetBotMoveTimer()

                    new_frame_advantage_calc = time_till_recovery_bot - time_till_recovery_opp

                    frameDataEntry.currentFrameAdvantage = frameDataEntry.WithPlusIfNeeded(new_frame_advantage_calc)

                    if gameState.IsBotBlocking():
                        frameDataEntry.onBlock = new_frame_advantage_calc
                    else:
                        if gameState.IsBotGettingCounterHit():
                            frameDataEntry.onCounterHit = new_frame_advantage_calc
                        else:
                            frameDataEntry.onNormalHit = new_frame_advantage_calc


                    frameDataEntry.hitRecovery = time_till_recovery_opp
                    frameDataEntry.blockRecovery = time_till_recovery_bot

                    if self.isPlayerOne:
                        prefix = "p1: "
                    else:
                        prefix = "p2: "

                    print(prefix + str(frameDataEntry))

                    #print(gameState.stateLog[-1].opp.startup)
                    #print(time_till_recovery_bot)

                    self.second_opinion = True
                    self.stored_bot_recovery = time_till_recovery_bot
                    self.stored_opp_recovery = time_till_recovery_opp
                    self.stored_prefix = prefix
                    self.stored_opp_id = opp_id
                    self.second_opinion_timer = 0

                    gameState.BackToTheFuture(self.active_frame_wait)

                    self.active_frame_wait = 1
                gameState.ReturnToPresent()
        if self.isPlayerOne:
            gameState.FlipMirror()

class FrameDataEntry:
    def __init__(self, print_extended = False):
        self.print_extended = print_extended
        self.move_id = '??'
        self.startup = '??'
        self.calculated_startup = -1
        self.hitType = '??'
        self.onBlock = '??'
        self.onCounterHit = '??'
        self.onNormalHit = '??'
        self.recovery = '??'
        self.damage = '??'
        self.blockFrames = '??'
        self.activeFrames = '??'
        self.currentFrameAdvantage = '??'
        self.currentActiveFrame = '??'
        self.input = '??'
        self.technical_state_reports = []
        self.blockRecovery = '??'
        self.hitRecovery = '??'

    def WithPlusIfNeeded(self, value):
        try:
            if value >= 0:
                return '+' + str(value)
            else:
                return str(value)
        except:
            return str(value)

    def InputTupleToInputString(self, inputTuple):
        s = ""
        for input in inputTuple:
            s += (input[0].name + input[1].name.replace('x', '+')).replace('N', '')
        #if input[2]:
            #s += "+RA"
        return s

    def __repr__(self):

        notes = ''



        self.calculated_startup = self.startup
        for report in self.technical_state_reports:
            #if not self.print_extended:
            if 'TC' in report.name and report.is_present():
                notes += str(report)
            elif 'TJ' in report.name and report.is_present():
                notes += str(report)
            elif 'PC' in report.name and report.is_present():
                notes += str(report)
            elif 'SKIP' in report.name and report.is_present():
                self.calculated_startup = str(self.startup - report.total_present() + 1) + '?'
            elif self.print_extended:
                if report.is_present():
                    notes += str(report)
        if self.print_extended:
            pass
            #notes += ' d_recovery {}'.format(self.blockRecovery)
            #notes += ' a_recovery {}'.format(self.hitRecovery)
            #notes += "Total:" + str(self.recovery) + "f "


        return "{:^5}|{:^8}|{:^9}|{:^8}|{:^5}|{:^5}|{:^5}|{} NOW:{}".format(
            str(self.input),
            str(self.hitType)[:7],
            str(self.calculated_startup),
            self.WithPlusIfNeeded(self.onBlock),
            self.WithPlusIfNeeded(self.onNormalHit),
            self.WithPlusIfNeeded(self.onCounterHit),
            (str(self.currentActiveFrame) + "/" + str(self.activeFrames)),
            notes,
            str(self.currentFrameAdvantage)
        )


        #return "" + str(self.input).rjust(len('input')) + " |" + str(self.hitType)[:7] +  "|" + str(self.calculated_startup).center(len('startup')) + "|" + str(self.damage).center(len('  damage ')) + "| " + self.WithPlusIfNeeded(self.onBlock).center(len('block')) + "|" \
               #+ self.WithPlusIfNeeded(self.onNormalHit) +  " |" + (str(self.currentActiveFrame) + "/" + str(self.activeFrames) ).center(len(' active ')) + '| ' + notes \
               #+ " NOW:" + str(self.currentFrameAdvantage)

                #+ " Recovery: " + str(self.recovery)
                # + " Block Stun: " + str(self.blockFrames)
                #" CH: " + self.WithPlusIfNeeded(self.onCounterHit) +
