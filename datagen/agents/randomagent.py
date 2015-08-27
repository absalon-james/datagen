import random
import time
import datagen.utils as utils


class RandomAgent(object):
    """
    Random simulated agent.

    """
    def __init__(self,
        name='randomagent',
        range_start=0,
        range_stop=100,
        max_points=None,
        duration=None,
        handlers=None,
        interval=1):
        """
        @param name - String name of agent
        @param range_start - Integer start of random range
        @param range_stop - Integer stop of random range
        @param max_points - Maximum number of points to generate
        @param duration - Integer number of seconds for agent to generate data
        @param handlers - List of handlers for point generation
        @param interval - Amount of seconds to wait between point generation
            can also be set to a function to generate number of seconds.

        @param stop - Integer stop of range

        """
        self.name = name
        self.range_start = int(range_start)
        self.range_stop = int(range_stop)
        self.max_points = max_points
        self.duration = duration

        if handlers is None:
            handlers = []
        self.handlers = handlers
        self.interval = interval

    def should_stop(self):
        """
        Checks for stopping conditions of agent.

        @return boolean
        """
        if self.max_points and self.points_so_far >= self.max_points:
            return True
        if self.duration and time.time() > self.start_time + self.duration:
            return True
        return False

    def wait(self):
        """
        Waits based on interval.

        """
        if callable(self.interval):
            self.interval()
        else:
            time.sleep(self.interval)

    def measure(self):
        """

        """
        point = {
            'time': utils.time_in_ms(),
            'value': random.randrange(self.range_start, self.range_stop),
            'name': self.name
        }
        self.points_so_far += 1
        return point

    def run(self):
        """

        """
        self.points_so_far = 0
        self.start_time = time.time()
        while True:
            point = self.measure()
            for h in self.handlers:
                h.handle(point)
            if self.should_stop():
                break
            self.wait()
