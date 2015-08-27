import pprint

from handler import Handler

class PrintHandler(Handler):
    """
    Simple handler that only prints data.

    """
    def handle(self, data):
        """
        Handles data. Only pretty prints.

        @param data - Dictionary

        """
        pprint.pprint(data)
