__author__ = 'Alan'

from Shell import *









class ActualGame(App):
    def build(self):
        return shell

if __name__=='__main__':
    ActualGame().run()