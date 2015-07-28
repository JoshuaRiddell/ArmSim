from PyQt4 import QtGui

SEQUENCE_ELEMENT_TYPES = [
	"NodeElement"
]

class _SequenceElement(object):
    def __init__(self, queue):
    	self.name = "UnNamed"
        self.queue_pos = queue_pos

    def delete_(self):
        pass

    def get_values(self, arm):
    	pass

    def set_values(self, arm):
    	pass

    def execute(self, arm):
        sleep(1)

class NodeElement(_SequenceElement):
	def __init__(self, queue):
		super().__init__(queue_pos)
		self.joints = {}
		self.name = "Node"

	def delete_(self):
		self.joints = {}

	def get_values(self, arm):
		pass