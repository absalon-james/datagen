import eventlet
eventlet.monkey_patch()
import copy
import time

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from handler import Handler


class ElasticsearchHandler(Handler):
    """
    Handles data for elasticsearch

    """
    def __init__(self, queue,
                 index_from_data=None, _index='datagen', _type='random'):
        """
        @param queue - eventlet.queue.Queue
        @param index_from_data - Callable. Specifies how to get index name
            from data
        @param _index - String name of the index to use if not
            viding index_from_data.
        @param _tipe - String type

        """
        self.queue = queue
        self._type = _type
        self._index = _index
        self.index_from_data = index_from_data

    def handle(self, data):
        """
        Puts data document on the write queue.

        @param data - Dictionary

        """
        data = copy.copy(data)
        if callable(self.index_from_data):
            _index = self.index_from_data(data)
        else:
            _index = self._index
        data.update(
            _index=_index,
            _type=self._type
        )
        self.queue.put(data)


class ElasticsearchQueue(object):
    """
    Works the elasticsearch queue for writes.

    """
    def __init__(self, interval, max_docs, client):
        """
        Inits the worker

        @param interval - Float time in seconds to wait when queue is empty
        @param max_docs - Integer maximum docs to write at a time
        @param client - Elasticsearch Client

        """
        self.interval = interval
        self.max_docs = max_docs
        self.client = client
        self.workers = []
        self.queue = eventlet.queue.Queue()

    def worker(self):
        """
        Spawns a worker

        """
        worker = eventlet.spawn(self.work)
        self.workers.append(worker)
        return worker

    def handler(self, index_from_data=None, _index='datagen', _type='random'):
        """
        Returns a handler for this queue.

        @param index_from_data
        @param _index
        @param _type
        @return ElasticsearchHandler

        """
        return ElasticsearchHandler(self.queue, index_from_data, _index, _type)

    def work(self):
        """
        Long running loop to write to elasticsearch

        """
        while True:
            # Start with empty array and add from queue
            docs = []
            for i in xrange(self.max_docs):
                try:
                    docs.append(self.queue.get(block=False))
                # Sleep for a time when empty
                except eventlet.queue.Empty:
                    time.sleep(self.interval)
                    break
            print "Gots %s docs" % len(docs)
            if docs:
                count, extra = bulk(self.client, docs)
                for d in docs:
                    self.queue.task_done()
