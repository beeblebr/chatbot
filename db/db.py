import conf

_client = None


def get_connection():
    global _client
    if not _client:
        _client = MongoClient(
            'mongo', username=conf.MONGO_USERNAME, password=conf.MONGO_PASSWORD)
    return _client.get_database('main')
