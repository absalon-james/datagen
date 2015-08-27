class Scenario(object):
    """
    Scenario base class

    Subclasses of scenario are expected to implement
    the methods setup, run, and teardown

    """
    def play(self):
        if hasattr(self, 'setup'):
            self.setup()
        if hasattr(self, 'run'):
            self.run()
        if hasattr(self, 'teardown'):
            self.teardown()
