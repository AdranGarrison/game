__author__ = 'Alan'

import Shell
import cProfile
import pstats











class ActualGame(Shell.App):
    def on_start(self):
        self.profile=cProfile.Profile()
        self.profile.enable()

    def on_stop(self):
        self.profile.disable()
        self.profile.print_stats(sort='time')


    def build(self):
        return Shell.shell

if __name__=='__main__':
    ActualGame().run()