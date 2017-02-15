import os
import unittest
import string
import random

from sqlalchemy.exc import IntegrityError

from recapi.server import app, db, init_api
from recapi.config import basedir
from recapi.models import DbLike
from recapi.cache import Cache, Like


LC = string.ascii_lowercase
UC = string.ascii_uppercase
USER_IDS = [a + b for a in UC for b in LC]
ITEM_IDS = [a + b for a in LC for b in LC]
LIKES = [Like(user, item) for user in USER_IDS for item in ITEM_IDS]

def random_like():
    return Like(random.choice(USER_IDS[:5]), random.choice(ITEM_IDS[:5]))

def random_likes(count):
    return random.sample(LIKES, count)

class TestCase(unittest.TestCase):
    def setUp(self):
        # app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///api'
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()
        init_api()

    def tearDown(self):
        db.session.remove()
        # with app.app_context():
        #     db.drop_all()

    def test_db_insert_unique(self):
        unique_likes = random_likes(1000)
        for user_id, item_id in unique_likes:
            like = DbLike(user_id, item_id)
            db.session.add(like)
        db.session.commit()
        res = [like.tuple for like in DbLike.query.all()]
        self.assertCountEqual(unique_likes, res)

    def test_cache_add_many(self):
        unique_likes = random_likes(1000)
        extra_likes = unique_likes[:10]
        cache = Cache(db)
        cache.add_many(unique_likes)
        cache.add_many(extra_likes)
        self.assertCountEqual(cache.likes, unique_likes)

    def test_cache_add(self):
        unique_likes = random_likes(20)
        extra_likes = unique_likes[:10]
        cache = Cache(db)
        for like in unique_likes + extra_likes:
            cache.add(like)
        self.assertCountEqual(cache.likes, unique_likes)

    def test_cache_persistence(self):
        unique_likes = random_likes(1000)
        Cache(db).add_many(unique_likes)
        cache = Cache(db)
        self.assertCountEqual(cache.likes, unique_likes)

    # def test_api(self):
    #     result = self.client.get('/v1/users/asdf')
    #     print('result: %s' % result.data.decode())

    def test_user_like_api_post(self):
        unique_likes = random_likes(20)
        extra_likes = unique_likes[:10]
        for user_id, item_id in unique_likes + extra_likes:
            result = self.client.post('/v1/likes/user/' + user_id + '/item/' + item_id, data={})
        self.assertEqual(len(DbLike.query.all()), len(unique_likes))

    def test_user_like_api_delete(self):
        unique_likes = random_likes(20)
        extra_likes = unique_likes[:10]
        for user_id, item_id in unique_likes:
            result = self.client.post('/v1/likes/user/' + user_id + '/item/' + item_id, data={})
        for user_id, item_id in extra_likes:
            result = self.client.delete('/v1/likes/user/' + user_id + '/item/' + item_id, data={})
        self.assertEqual(len(DbLike.query.all()), len(unique_likes) - len(extra_likes))

    # def test_db_insert(self):
    #     for i in range(100000):
    #         like = DbLike(*random_like())
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
