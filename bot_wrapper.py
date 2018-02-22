"""Helper functions to interact with the bot.

This module initializes the `Agent` and provides functions to abstract away concerns regarding
the fetching of trackers and slots.

"""
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.agent import Agent
from rasa_core.domain import TemplateDomain
from rasa_core.events import SlotSet

from rasa_utils import TrackerWrapper

from search_knowledge_policy import SearchKnowledgePolicy

agent = Agent(TemplateDomain.load('code/domain.yml'),
              policies=[SearchKnowledgePolicy()],
              interpreter=RasaNLUInterpreter("models/default/current"))


def get_slots_of_user(user_id):
    """Returns the slot values for a user.

    Args:
        user_id: Eight ID of user.

    Returns:
        User's slots.
    """
    tracker = agent.tracker_store.get_or_create_tracker(user_id)
    return tracker.slots


def handle_response(**response_metadata):
    user_id = response_metadata['user_id']
    tracker = agent.tracker_store.get_or_create_tracker(user_id)
    if tracker.slots['response_metadata'].value:
        old_response_metadata = tracker.slots['response_metadata'].value
        old_response_metadata.update(response_metadata)
        tracker.update(SlotSet('response_metadata', old_response_metadata))
    else:
        tracker.update(SlotSet('response_metadata', response_metadata))
    agent.tracker_store.save(tracker)
    response = agent.handle_message(
        u'Who works on machine learning?', sender_id=user_id)
    tracker = agent.tracker_store.get_or_create_tracker(user_id)
    logger.info(tracker.slots)
    return response, tracker.slots
