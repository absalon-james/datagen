import eventlet
eventlet.monkey_patch()

import argparse
import elasticsearch
import random
import time

import agents
import handlers


def interval():
    """
    Generates a random float and then sleeps for that value in seconds.

    """
    time.sleep(random.uniform(0, 2.0))


def parse_args():
    """
    Simple argument parser

    """
    parser = argparse.ArgumentParser(description="Simulated metric gathering")
    parser.add_argument('agents', type=int, help="Number of agents")
    parser.add_argument('points', type=int, help="Number of points per agent")
    return parser.parse_args()


args = parse_args()
pool = eventlet.greenpool.GreenPool()

client = elasticsearch.Elasticsearch(['192.168.4.22'])
es_queue = handlers.es.ElasticsearchQueue(0.2, 1000, client)
es_queue.worker()
es_queue.worker()
es_queue.worker()
es_queue.worker()

h = []
#h.append(handlers.PrintHandler())
h.append(es_queue.handler())

agents = [agents.Random(
            name='agent.random.%s' % (i + 1),
            range_start=0,
            range_stop=100,
            handlers=h,
            interval=0.0,
            max_points=args.points) for i in xrange(args.agents)]

start = time.time()
for agent in agents:
    pool.spawn(agent.run)
pool.waitall()

es_queue.queue.join()

elapsed = time.time() - start
points = sum([getattr(agent, 'points_so_far') for agent in agents])
print "Pushed %s points in %s seconds." % (points, elapsed)
