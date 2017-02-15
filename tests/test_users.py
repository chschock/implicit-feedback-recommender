import os
import unittest
import string
import random

# from psycopg2 import IntegrityError
# import psycopg2
from sqlalchemy.exc import IntegrityError

from recapi.config import basedir
from recapi.server import app, db
from recapi.models import Like
from recapi.cache import Cache

LC = string.ascii_lowercase
UC = string.ascii_uppercase
USER_IDS = [a + b for a in UC for b in LC]
ITEM_IDS = [a + b for a in LC for b in LC]
LIKES = [(user, item) for user in USER_IDS for item in ITEM_IDS]

def random_like():
    return random.choice(USER_IDS[:5]), random.choice(ITEM_IDS[:5])

def random_likes(count):
    return random.sample(LIKES, count)

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///api'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        # db.drop_all()

    def test_db_insert_unique(self):
        for user_id, item_id in random_likes(1000):
            like = Like(user_id, item_id)
            db.session.add(like)
        db.session.commit()
        res = [like.tuple for like in Like.query.all()]
        print('%d likes in db.' % len(res))
        print(list(res)[:4])

    def test_cache_add_many(self):
        unique_likes = random_likes(1000)
        extra_likes = unique_likes[:10]
        cache = Cache(db)
        cache.add_many(unique_likes)
        cache.add_many(extra_likes)
        self.assertEqual(len(cache), len(unique_likes))

    def test_cache_add(self):
        unique_likes = random_likes(20)
        extra_likes = unique_likes[:10]
        cache = Cache(db)
        for like in unique_likes + extra_likes:
            cache.add(like)
        self.assertEqual(len(cache), len(unique_likes))

    def test_cache_persistence(self):
        unique_likes = random_likes(1000)
        Cache(db).add_many(unique_likes)
        cache = Cache(db)
        self.assertEqual(len(cache), len(unique_likes))


    # def test_db_insert(self):
    #     for i in range(100000):
    #         like = Like(*random_like())
    #         db.session.add(like)
    #     try:
    #         db.session.commit()
    #     except IntegrityError:
    #         pass



    # def test_make_unique_nickname(self):
    #     u = User(nickname='john', email='john@example.com')
    #     db.session.add(u)
    #     db.session.commit()
    #     nickname = User.make_unique_nickname('john')
    #     assert nickname != 'john'
    #     u = User(nickname=nickname, email='susan@example.com')
    #     db.session.add(u)
    #     db.session.commit()
    #     nickname2 = User.make_unique_nickname('john')
    #     assert nickname2 != 'john'
    #     assert nickname2 != nickname
