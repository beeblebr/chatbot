class TrackerWrapper:
    def __init__(self, slots):
        self.slots = slots

    def __getitem__(self, key):
        return self.slots[u'response_metadata'].value[key]

    def __setitem__(self, key, item):
        self.slots[u'response_metadata'].update(key=item)
