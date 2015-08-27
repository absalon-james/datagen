import pprint
import scenario
from elasticsearch import Elasticsearch


class ElasticsearchScenario(scenario.Scenario):
    """
    Runs through an elastic search scenario

    """
    def __init__(self, client):
        """
        Inits the elastic search client.

        """
        self.client = client

    def setup(self):
        """
        Creates all indexes

        """
        pass

    def run(self):
        pass

    def teardown(self):
        """
        Deletes all indices

        """
        print "Deleting all indexes"
        resp = self.client.indices.delete(index='*')
        print dir(resp)


if __name__ == '__main__':
    es_host = '192.168.4.22'
    client = Elasticsearch([es_host])
    s = ElasticsearchScenario(client)

    n_shards = 3
    n_replicas = 0

    resp = client.indices.put_template(
        name='datagen-template',
        order=1,
        body={
            "template": "datagen-*",
            "settings": {
                'number_of_shards': n_shards,
                'number_of_replicas': n_replicas
            },
            "mappings": {
                "random": {
                    '_timestamp': {
                        'enabled': True,
                        'path': 'time'
                    }
                }
            }
        }
    )

    pprint.pprint(resp)
    s.play()
