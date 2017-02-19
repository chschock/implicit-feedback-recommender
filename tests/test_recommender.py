import os
import unittest
import string
import random
import time
import json

from flask import Flask, current_app
from recapi.server import create_app, reset_cache
from recapi.config import TestingConfig
from recapi.extensions import db, api
from recapi.models import DbLike
from recapi.cache import Cache, Like

LC = string.ascii_lowercase[:10]
UC = string.ascii_uppercase[:10]
USER_IDS = [a + b + c for a in UC for b in LC for c in LC]
ITEM_IDS = [a + b for a in LC for b in LC]
LIKES = [Like(user, item) for user in USER_IDS for item in ITEM_IDS]

def random_like():
    return Like(random.choice(USER_IDS[:5]), random.choice(ITEM_IDS[:5]))

def random_likes(count):
    return random.sample(LIKES, count)

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.session.remove()
        db.drop_all()
        db.create_all()
        reset_cache(self.app)
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        api.resources.clear()
        self.app_context.pop()

class CacheTestCase(FlaskTestCase):

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


class LikesTestCase(FlaskTestCase):

    def test_likes_api_post(self):
        unique_likes = random_likes(20)
        extra_likes = unique_likes[:10]
        for user_id, item_id in unique_likes + extra_likes:
            result = self.client.post('/v1/likes/user/' + user_id + '/item/' + item_id, data={})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(DbLike.query.all()), len(unique_likes))

    def test_likes_api_delete(self):
        unique_likes = random_likes(20)
        extra_likes = unique_likes[:10]
        for user_id, item_id in unique_likes:
            result = self.client.post('/v1/likes/user/' + user_id + '/item/' + item_id, data={})
        for user_id, item_id in extra_likes:
            result = self.client.delete('/v1/likes/user/' + user_id + '/item/' + item_id, data={})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(DbLike.query.all()), len(unique_likes) - len(extra_likes))

    def test_likes_bulk_api_post(self):
        unique_likes = random_likes(20)
        extra_likes = unique_likes[:10]
        data = {'likes':
            [(l.user_id, l.item_id) for l in unique_likes + extra_likes]
        }
        result = self.client.post('/v1/likes/bulk',
            data=json.dumps(data),
            headers={'content-type':'application/json'})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(DbLike.query.all()), len(unique_likes))

    def test_likes_bulk_api_post_empty(self):
        data = {'likes': []}
        result = self.client.post('/v1/likes/bulk',
            data=json.dumps(data),
            headers={'content-type':'application/json'})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(DbLike.query.all()), 0)

class RecommenderTestCase(FlaskTestCase):

    def setUp(self):
        super().setUp()
        cache = Cache(db)
        for i in range(10):
            cache.add_many(random_likes(50))
        self.likes = list(cache.likes)
        reset_cache(self.app)

    def _check_response(self, response, count):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.data.decode())), count)

    def test_recommendations_api_count(self):
        res = self.client.get(
            '/v1/recommendations/user/{}'.format(self.likes[0].user_id))
        self._check_response(res, current_app.config['RECOMMENDER_DEFAULT_COUNT'])
        for i, count in enumerate(range(100, 5)):
            res = self.client.get(
                '/v1/recommendations/user/{}?count={}'.format(
                    self.likes[i].user_id, count))
            self._check_response(res, count)
        res = self.client.get('/v1/recommendations/user/asdf?count=-1')
        self.assertEqual(res.status_code, 404)

    def test_recommendations_api_user(self):
        res = self.client.get('/v1/recommendations/user/()(123')
        self.assertEqual(res.status_code, 404)

class MaintenanceTestCase(FlaskTestCase):

    def test_maintenance_api(self):
        result = self.client.delete('/v1/maintenance/delete-all-data')
        self.assertEqual(result.status_code, 200)
