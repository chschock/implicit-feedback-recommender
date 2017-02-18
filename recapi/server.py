import os
from flask import Flask, current_app
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

ID_REGEX = re.compile(r'[a-zA-Z0-9\-_]+')

def abort_if_no_id(string, hint):
    if ID_REGEX.match(string) is None and False:
        abort(404, message="'{}' is not valid {}".format(string, hint))

class LikesAPI(Resource):

    def post(self, user_id, item_id):
        abort_if_no_id(user_id, 'user_id')
        abort_if_no_id(user_id, 'item_id')
        current_app.cache.add(Like(user_id, item_id))

    def delete(self, user_id, item_id):
        abort_if_no_id(user_id, 'user_id')
        abort_if_no_id(user_id, 'item_id')
        current_app.cache.delete(Like(user_id, item_id))

def abort_if_no_likes(likes):
    for like in likes:
        if not isinstance(like, list):
            abort(404, message="{} is not a list".format(like))
        if not len(like) == 2:
            abort(404, message="{} is not of length 2".format(like))
        abort_if_no_id(like[0], 'bulk user_id')
        abort_if_no_id(like[1], 'bulk item_id')

class LikesBulkAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('likes', type=list, required=True, location='json')
        super().__init__()

    def post(self):
        args = self.reqparse.parse_args()
        abort_if_no_likes(args['likes'])
        likes = [Like(pair[0], pair[1]) for pair in args['likes']]
        current_app.cache.add_many(likes)

class RecommendationsAPI(Resource):

    def get(self, user_id):
        abort_if_no_id(user_id, 'user_id')
        rmdr = current_app.cache.build_recommender()
        result = rmdr.recommend(user_id, 10, alpha=2, beta=0.5)
        return jsonify(result)

api.add_resource(LikesAPI, '/v1/likes/user/<string:user_id>/item/<string:item_id>', endpoint='likes')
api.add_resource(LikesBulkAPI, '/v1/likes/bulk', endpoint='likes_bulk')
api.add_resource(RecommendationsAPI, '/v1/recommendations/user/<string:user_id>', endpoint='recommendations')

def init_api():
    with app.app_context():
        current_app.cache = Cache(db)

if __name__ == '__main__':
    init_api()
    app.run(debug = True)
