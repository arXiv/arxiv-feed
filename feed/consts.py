from enum import Enum


class FeedVersion(str, Enum):
    RSS_2_0 = "rss-2.0"
    ATOM_1_0 = "atom-1.0"


FEED_NUM_DAYS = 1


DELIMITER = "+"
