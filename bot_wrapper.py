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
    tracker.update(SlotSet('response_metadata', response_metadata))
    agent.tracker_store.save(tracker)

    response = agent.handle_message(u'Who works on machine learning?', sender_id=user_id)
    tracker = agent.tracker_store.get_or_create_tracker(user_id)
    logger.info(tracker.slots)
    return response, tracker.slots


# def handle_query(user_id, q):
#     """Calls `agent.handle_message` with the `user_id` populated into the slot and returns the
#     response.

#     Args:
#         user_id: Eight ID of user.
#         q: User query.

#     Returns:
#         tuple: Response and slots.
#     """
#     # Insert user_id to the bot's slots
#     tracker = agent.tracker_store.get_or_create_tracker(user_id)
#     tracker.update(SlotSet('user_id', user_id))
#     tracker.update(SlotSet('query', q))
#     tracker.update(SlotSet('intent', 'QUERY'))
#     agent.tracker_store.save(tracker)

#     response = agent.handle_message(None, sender_id=user_id)
#     tracker = agent.tracker_store.get_or_create_tracker(user_id)
#     return response, tracker.slots


# def handle_query_clarification(
#     user_id,
#     query_clarification_option_selected
# ):
#     tracker = agent.tracker_store.get_or_create_tracker(user_id)
#     tracker.update(SlotSet('query_clarification_option_selected', query_clarification_option_selected))
#     tracker.update(SlotSet('intent', 'QUERY_CLARIFICATION'))
#     agent.tracker_store.save(tracker)

#     response = agent.handle_message(None, sender_id=user_id)
#     tracker = agent.tracker_store.get_or_create_tracker(user_id)
#     return response, tracker.slots


# def handle_corpus_search(user_id):
#     tracker = agent.tracker_store.get_or_create_tracker(user_id)
#     tracker.update(SlotSet('intent', 'CORPUS_SEARCH'))
#     agent.tracker_store.save(tracker)

#     response = agent.handle_message(None, sender_id=user_id)
#     tracker = agent.tracker_store.get_or_create_tracker(user_id)
#     return response, tracker.slots


# def handle_corpus_clarification(
#     user_id,
#     corpus_clarification_option_selected
# ):
#     tracker = agent.tracker_store.get_or_create_tracker(user_id)
#     tracker.update(SlotSet('corpus_clarification_option_selected', corpus_clarification_option_selected))
#     tracker.update(SlotSet('intent', 'CORPUS_CLARIFICATION'))
#     agent.tracker_store.save(tracker)

#     response = agent.handle_message(None, sender_id=user_id)
#     tracker = agent.tracker_store.get_or_create_tracker(user_id)
#     return response, tracker.slots
