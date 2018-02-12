from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.agent import Agent
from rasa_core.domain import TemplateDomain
from rasa_core.events import SlotSet

from search_knowledge_policy import SearchKnowledgePolicy

agent = Agent(TemplateDomain.load('domain.yml'), policies=[SearchKnowledgePolicy()], interpreter=RasaNLUInterpreter("models/default/current"))

def handle_message(user_id, q):
    """Calls `agent.handle_message` with the `user_id` populated into the slot and returns the response.

    Args:
        user_id: Eight ID of user.
        q: User query.

    Returns:
        tuple: 
    """
    # Insert user_id to the bot's slots
    tracker = agent.tracker_store.get_or_create_tracker(user_id)
    tracker.update(SlotSet('user_id', user_id))
    agent.tracker_store.save(tracker)

    response = agent.handle_message(unicode(q), sender_id=user_id)
    tracker = agent.tracker_store.get_or_create_tracker(user_id)
    return response, tracker.slots
