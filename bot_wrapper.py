from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.agent import Agent
from rasa_core.events import SlotSet

from util.chat_utils import get_all_topics

agent = Agent.load("models/dialogue", interpreter=RasaNLUInterpreter("models/default/current"))


def handle_message(user_id, q):
    # Insert user_id to the bot's slots
    tracker = agent.tracker_store.get_or_create_tracker(user_id)
    tracker.update(SlotSet('user_id', user_id))
    
    agent.tracker_store.save(tracker)
    response = agent.handle_message(unicode(q), sender_id=user_id)

    tracker = agent.tracker_store.get_or_create_tracker(user_id)

    return response, tracker.slots
