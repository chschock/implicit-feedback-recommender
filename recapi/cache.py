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

from collections import namedtuple
Like = namedtuple('Like', 'user_id item_id')

class Cache(object):
    def __init__(self, db):
        self.likes = set([like.tuple for like in DbLike.query.all()])
        self.db = db

    def add_many(self, likes):
        for like in likes:
            assert isinstance(like, Like)
            if like not in self.likes:
                self.db.session.add(DbLike(*like))

        self.db.session.commit()
        self.likes.update(likes)

    def add(self, like):
        assert isinstance(like, Like)
        if like in self.likes:
            return
        self.db.session.add(DbLike(*like))
        self.db.session.commit()
        self.likes.add(like)

    def delete(self, like):
        assert isinstance(like, Like)
        if like in self.likes:
            DbLike.query.filter_by(
                user_id=like.user_id, item_id=like.item_id).delete()
            self.db.session.commit()
            self.likes.discard(like)


    def __len__(self):
        return len(self.likes)
