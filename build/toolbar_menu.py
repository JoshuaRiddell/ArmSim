#   ArmSim                                                             #
#   By: Joshua Riddell                                                 #
#                                                                      #
#  Permission is hereby granted, free of charge, to any person         #
#  obtaining a copy of this software and associated documentation      #
#  files (the "Software"), to deal in the Software without             #
#  restriction, including without limitation the rights to use,        #
#  copy, modify, merge, publish, distribute, sublicense, and/or sell   #
#  copies of the Software, and to permit persons to whom the           #
#  Software is furnished to do so.                                     #
#                                                                      #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,     #
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES     #
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND            #
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR        #
#  ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF      #
#  CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION  #
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.     #


from pyglet_gui.option_selectors import Dropdown
from pyglet_gui.controllers import Option, Selector


class MenuDropdown(Dropdown):
    """ Defines a dropdown object which acts like the standard dropdown menus
    usually in the top bar of the window
    """

    def __init__(self, options, **kwargs):
        super().__init__(options, **kwargs)
        self.options = options

    def select(self, option_name):
        """ Called when an option in the dropdown is selected.

        select(str) -> None
        """
        Selector.select(self, option_name)
        Selector.select(self, self.options[0])
        self._delete_pulldown_menu()
        self.reload()
        self.reset_size()
        self.layout()
