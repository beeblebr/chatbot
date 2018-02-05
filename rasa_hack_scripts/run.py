from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.agent import Agent
from rasa_core.trackers import DialogueStateTracker
from rasa_core.slots import TextSlot
from rasa_core.events import SlotSet
from rasa_core.tracker_store import *

agent = Agent.load("models/dialogue",
                   interpreter=RasaNLUInterpreter("models/default/current"))

if __name__ == '__main__':
    while True:
        msg = raw_input('>> ')
        print('You said', msg)
        print(agent.handle_message(unicode(msg)))
