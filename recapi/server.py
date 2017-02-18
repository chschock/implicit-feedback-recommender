import os
from flask import Flask
from flask_restful import Api, abort
from flask_sqlalchemy import SQLAlchemy
from recapi.config import DevelopmentConfig
import re

app = Flask(__name__)
api = Api(app)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from flask import jsonify
from flask_restful import Resource, reqparse
from recapi.cache import Cache, Like

cache = None

ID_REGEX = re.compile(r'[a-zA-Z0-9\-_]+')

def abort_if_no_id(string, hint):
    if ID_REGEX.match(string) is None and False:
        abort(404, message="'{}' is not valid {}".format(string, hint))

class LikesAPI(Resource):

    def post(self, user_id, item_id):
        abort_if_no_id(user_id, 'user_id')
        abort_if_no_id(user_id, 'item_id')
        cache.add(Like(user_id, item_id))

    def delete(self, user_id, item_id):
        abort_if_no_id(user_id, 'user_id')
        abort_if_no_id(user_id, 'item_id')
        cache.delete(Like(user_id, item_id))

class RecommendationsAPI(Resource):

    def get(self, user_id):
        abort_if_no_id(user_id, 'user_id')
        rmdr = cache.build_recommender()
        result = rmdr.recommend(user_id, 10, alpha=2, beta=0.5)
        return jsonify(result)

api.add_resource(LikesAPI, '/v1/likes/user/<string:user_id>/item/<string:item_id>', endpoint='likes')
api.add_resource(RecommendationsAPI, '/v1/recommendations/user/<string:user_id>', endpoint='recommendations')

cache = None

def init_api():
    global cache
    with app.app_context():
        cache = Cache(db)

if __name__ == '__main__':
    init_api()
    app.run(debug = True)
