from PyQt4 import QtGui


class Effector(object):
    """ Defines the robotic arm
    """

    def __init__(self, **kwargs):
        """ Initialises arm values.
        """
        pass

    def load_arm(self, arm_dictionary):
        self.members = {}
        for member in arm_dictionary["MEMBERS"]:
            self.members[member[0]] = member[1:]
        self.chains = arm_dictionary["VECTOR_CHAINS"]

        print(self.chains, self.members)
