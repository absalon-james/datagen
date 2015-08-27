class Handler(object):
    """
    Base class for handlers

    """
    def handle(self, data):
        """
        Subclasses should implement their own versions of this method.

        @param data - Dictionary

        """
        raise Exception("You oaf. You didn't implement the handle method")
