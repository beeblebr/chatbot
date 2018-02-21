import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrackerWrapper:
    def __init__(self, slots):
        self.slots = slots

    def __getitem__(self, key):
        return self.slots[u'response_metadata'].value[key]

    def __setitem__(self, key, value):
        item = {key: value}
        self.slots[u'response_metadata'].value.update(item)
        logger.info('hola: %s', self.slots['response_metadata'].value)
