import time
from datetime import datetime, timedelta
import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import conf

from util.db_utils import get_questions_since
from util.topic_utils import get_all_topics
from zscore import zscore

WINDOW_IN_MINUTES = 30
NUM_DAYS_HISTORY = 7


def bucketize_history(history, start_date):
    """Bucketizes all questions asked from the past NUM_DAYS_HISTORY days into intervals of WINDOW_IN_MINUTES minutes."""
    # Obtain questions asked in past week
    buckets = [[]
               for _ in range(NUM_DAYS_HISTORY * 24 * 60 / WINDOW_IN_MINUTES)]
    for h in history:
        periods_passed = int(
            (h['timestamp'] - start_date).total_seconds() / 60) / WINDOW_IN_MINUTES
        buckets[periods_passed].append(h)
    return buckets


DECAY_HALF_LIFE = 4.0
MIN_THRESHOLD = 0.05  # Any weighted value less than this will not be considered


def weighted_decay_sum(counts, verbose=False):
    """Computes a weighted sum of the mention counts using an exponential decay function."""
    sum = 0
    for i in reversed(range(len(counts))):
        if verbose:
            if (len(counts) - i - 1) < 10:
                print('difference: ' + str(len(counts) - i - 1))

        # -1 to correct for zero-indexing
        exponent = (len(counts) - i - 1) / DECAY_HALF_LIFE
        decayed_val = counts[i] * (0.5 ** exponent)
        if verbose:
            if (len(counts) - i - 1) < 10:
                print(decayed_val)
                print('\n')
        sum += decayed_val
    return sum


def identify_trending_topics():
    current_date = datetime.now()
    start_date = current_date - timedelta(days=NUM_DAYS_HISTORY)

    history = list(get_questions_since(start_date))
    current_date = datetime.now()

    buckets = bucketize_history(history, current_date)

    def flatten(l): return [item for sublist in l for item in sublist]
    all_topics = set(flatten(
        [get_all_topics(x['transformed_text'], transformed=True) for x in history]))

    topic_wise_counts = {}
    for topic in all_topics:
        num_mentions = []
        for questions in buckets:
            num_mentions.append(
                len([x for x in questions if topic in x['transformed_text']]))
        topic_wise_counts[topic] = num_mentions

    from pprint import pprint
    # for topic in topic_wise_counts:
    #     print(topic)
    #     print('============================')
    #     print(['_' if x == 0 else x for x in topic_wise_counts[topic]])
    #     print('\n\n\n')

    topic_wise_scores = {}
    for topic in topic_wise_counts:
        counts = topic_wise_counts[topic]
        z_model = zscore(counts)
        # print(topic)
        # print('==========')
        # print(z_model.avg())
        # print(weighted_decay_sum(counts, 'chair' in topic))
        # print('\n\n')
        topic_wise_scores[topic] = z_model.score(weighted_decay_sum(counts))

    return topic_wise_scores


# if __name__ == '__main__':
identify_trending_topics()

# scheduler = BackgroundScheduler()
# scheduler.start()
# scheduler.add_job(
#     func=lambda : identify_trending_topics(corpus),
#     trigger=IntervalTrigger(hours=2),
#     id='trending_topics_job',
#     name='Identify trending topics every 2 hours',
#     replace_existing=True)
# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())
