import os
from flask import Flask
from flask_restful import Api, abort
from flask_sqlalchemy import SQLAlchemy

from recapi.config import DevelopmentConfig

from recapi.database import init_db

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

# api.add_resource(UserAPI, '/v1/users/<string:user_id>', endpoint='user')
api.add_resource(LikesAPI, '/v1/likes/user/<string:user_id>/item/<string:item_id>', endpoint='userlike')

cache = None

def init_api():
    global cache
    with app.app_context():
        cache = Cache(db)

if __name__ == '__main__':
    init_api()
    app.run(debug = True)


# class UserListAPI(Resource):
#     def __init__(self):
#         self.reqparse = reqparse.RequestParser()
#         self.reqparse.add_argument('page', type=int, required=False, location='json')
#         self.reqparse.add_argument('n_results', type=int, required=False, location='json')
#         super(UserListAPI, self).__init__()
#
#     def get(self):
#         return jsonify(users.keys())
#
# api.add_resource(UserListAPI, '/v1/users', endpoint='users')

# class UserAPI(Resource):
#     def __init__(self):
#         self.reqparse = reqparse.RequestParser()
#         self.reqparse.add_argument('user_id', type=str, location='json')
#         super(UserAPI, self).__init__()
#
#     def get(self, user_id):
#         return jsonify(len(cache))
#         # return jsonify('hello')
#
#     def delete(self, user_id):
#         args = self.reqparse.parse_args()
#         if user_id not in users:
#             abort(404)
#         del users[user_id]
#         return jsonify( { 'user': user_id } )

# class UserLikeListAPI(Resource):
#     def __init__(self):
#         self.reqparse = reqparse.RequestParser()
#         self.reqparse.add_argument('page', type=int, required=False, location='json')
#         self.reqparse.add_argument('n_results', type=int, required=False, location='json')
#         super(UserListAPI, self).__init__()
#
#     def get(self):
#         args = self.reqparse.parse_args()
#         if user_id not in users:
#             abort(404)
#         return jsonify(list(users[user_id]))
#
# api.add_resource(UserLikeListAPI, '/v1/users/<string:user_id>/likes', endpoint='userlikes')
