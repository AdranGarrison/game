__author__ = 'Alan'

from Shell import *
import cProfile
import pstats










class ActualGame(App):
    def on_start(self):
        self.profile=cProfile.Profile()
        self.profile.enable()

    def on_stop(self):
        self.profile.disable()
        self.profile.print_stats(sort='time')


    def build(self):
        return shell

if __name__=='__main__':
    ActualGame().run()