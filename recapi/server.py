import os
from flask import Flask
from flask_restful import Api, abort
from flask_sqlalchemy import SQLAlchemy
from recapi.config import DevelopmentConfig

app = Flask(__name__)
api = Api(app)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from flask import jsonify
from flask_restful import Resource, reqparse
from recapi.cache import Cache, Like

cache = None
users = dict()


class LikesAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        # self.reqparse.add_argument('user_id', type=str, required=True, location='json')
        # self.reqparse.add_argument('like_id', type=str, location='json')
        super(LikesAPI, self).__init__()

    def post(self, user_id, item_id):
        args = self.reqparse.parse_args()
        cache.add(Like(user_id, item_id))

    def delete(self, user_id, item_id):
        args = self.reqparse.parse_args()
        cache.delete(Like(user_id, item_id))

class RecommendationsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        # self.reqparse.add_argument('user_id', type=str, required=True, location='json')
        # self.reqparse.add_argument('like_id', type=str, location='json')
        super(RecommendationsAPI, self).__init__()

    def get(self, user_id):
        args = self.reqparse.parse_args()
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
