from evennia import CmdSet

class VampireCommandSet(CmdSet):
    key = "VampireCommandSet"
    def at_cmdset_creation(self):
        # Leave empty or add common vampire commands applicable to all vampires
        pass
