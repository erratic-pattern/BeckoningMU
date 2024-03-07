from evennia import CmdSet

class VampireCommandSet(CmdSet):
    key = "VampireCommandSet"
    def at_cmdset_creation(self):
        self.add(CmdSetStatus())
        self.add(CmdCheckStatus())
        self.add(CmdSetAge())
        self.add(CmdSetTitle())
        self.add(CmdGrantStatusPoints())
        self.add(CmdAdjustStatus())
        self.add(CmdStatusBoard())
        pass
