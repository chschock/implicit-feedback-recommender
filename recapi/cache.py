from collections import namedtuple, defaultdict
import numpy as np
from .models import DbLike
from .recommender import Recommender
import time
Like = namedtuple('Like', 'user_id item_id')

REBUILD_RECOMMENDER_CHANGE_THRESHOLD = 100

class Cache(object):
    """
    Cache serves as in memory structure mirroring all data that is also
    persisted in the database. In the cache, data is stored in a normalized
    form, ready to be converted to a Recommender object, which is also stored
    in the cache. When the recommender is out of date in terms of the number
    of changes made to the data model, it is rebuilt on request.
    """
    def __init__(self, db):
        self.db = db
        self.user_map = defaultdict(lambda: len(self.user_map))
        self.item_map = defaultdict(lambda: len(self.item_map))

        self.likes = set([Like(*like.tuple) for like in DbLike.query.all()])
        self.user_ics = [self.user_map[like.user_id] for like in self.likes]
        self.item_ics = [self.item_map[like.item_id] for like in self.likes]
        self.ratings = [1] * len(self.likes)

        self.recommender = None
        self.changes = 0

    def add_many(self, likes):
        new_likes = [like for like in set(likes) if like not in self.likes]
        for like in new_likes:
            assert isinstance(like, Like)
            if like not in self.likes:
                self.db.session.add(DbLike(*like))
        self.db.session.commit()

        self.likes.update(new_likes)
        self.user_ics.extend([self.user_map[like.user_id] for like in new_likes])
        self.item_ics.extend([self.item_map[like.item_id] for like in new_likes])
        self.ratings.extend([1] * len(new_likes))
        self.changes += len(new_likes)

    def add(self, like):
        assert isinstance(like, Like)
        if like not in self.likes:
            self.db.session.add(DbLike(*like))
            self.db.session.commit()

            self.likes.add(like)
            self.user_ics.append(self.user_map[like.user_id])
            self.item_ics.append(self.item_map[like.item_id])
            self.ratings.append(1)
            self.changes += 1

    def delete(self, like):
        assert isinstance(like, Like)
        if like in self.likes:
            DbLike.query.filter_by(
                user_id=like.user_id, item_id=like.item_id).delete()
            self.db.session.commit()

            self.likes.discard(like)
            self.user_ics.append(self.user_map[like.user_id])
            self.item_ics.append(self.item_map[like.item_id])
            self.ratings.append(-1)
            self.changes += 1

    def __len__(self):
        return len(self.likes)

    def out_of_date(self):
        return (self.recommender is None or
            self.changes >= REBUILD_RECOMMENDER_CHANGE_THRESHOLD)

    def build_recommender(self):
        if not self.out_of_date():
            return self.recommender

        user_ics = np.array(self.user_ics, dtype=np.uint32)
        item_ics = np.array(self.item_ics, dtype=np.uint32)
        ratings = np.array(self.ratings, dtype=np.int32)
        users, items = [None] * len(self.user_map), [None] * len(self.item_map)
        for user_id, pos in self.user_map.items():
            users[pos] = user_id
        for item_id, pos in self.item_map.items():
            items[pos] = item_id
        kwargs = dict(min_item_freq=5, min_user_freq=1)
        self.recommender = Recommender(user_ics, item_ics, ratings, users, items, **kwargs)
        return self.recommender
