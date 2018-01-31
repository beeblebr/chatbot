from rasa_core.policies.policy import Policy
from rasa_core.actions.action import ACTION_LISTEN_NAME
from rasa_core import utils
import numpy as np

class SearchKnowledgePolicy(Policy):

    def predict_action_probabilities(self, tracker, domain):
    	if tracker.latest_action_name == ACTION_LISTEN_NAME:
    		return utils.one_hot(domain.action_names.index('action_search_knowledge_base'), domain.num_actions)
    	else:
    		return np.zeros(domain.num_actions)