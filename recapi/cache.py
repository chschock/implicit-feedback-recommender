from .models import DbLike

# from sqlalchemy.dialects.postgresql import insert
# from sqlalchemy import MetaData
#
# def insert_ignore(table, likes):
#     values = [dict(user_id=u, item_id=i) for u, i in likes]
#     insert_stmt = insert('likes').values(values
#         ).on_conflict_do_nothing(index_elements=['user_id','item_id'])
#     return insert_stmt

    # stmt = insert_ignore('likes', likes)
    # values = [dict(user_id=u, item_id=i) for u, i in likes]
    # stmt = insert('likes').values([{'user_id': 'qwe', 'item_id': 'bnm'}])
    # self.db.engine.execute(stmt)

from collections import namedtuple, defaultdict
Like = namedtuple('Like', 'user_id item_id')

class Cache(object):
    def __init__(self, db):
        self.db = db
        self.user_map = defaultdict(lambda: len(self.user_map))
        self.item_map = defaultdict(lambda: len(self.item_map))

        self.likes = set([Like(*like.tuple) for like in DbLike.query.all()])
        self.user_ics = [self.user_map[like.user_id] for like in self.likes]
        self.item_ics = [self.item_map[like.item_id] for like in self.likes]
        self.ratings = [1] * len(self.likes)

    def add_many(self, likes):
        for like in likes:
            assert isinstance(like, Like)
            if like not in self.likes:
                self.db.session.add(DbLike(*like))
        self.db.session.commit()

        new_likes = [like for like in likes if like not in self.likes]
        self.likes.update(new_likes)
        self.user_ics.extend([self.user_map[like.user_id] for like in new_likes])
        self.item_ics.extend([self.item_map[like.item_id] for like in new_likes])
        self.ratings.extend([1] * len(new_likes))

    def add(self, like):
        assert isinstance(like, Like)
        if like not in self.likes:
            self.db.session.add(DbLike(*like))
            self.db.session.commit()

            self.likes.add(like)
            self.user_ics.append(self.user_map[like.user_id])
            self.item_ics.append(self.item_map[like.item_id])
            self.ratings.append(1)

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

    def __len__(self):
        return len(self.likes)
