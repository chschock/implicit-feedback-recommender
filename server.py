from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)


users = dict()

class UserListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('page', type=int, required=False, location='json')
        self.reqparse.add_argument('n_results', type=int, required=False, location='json')
        super(UserListAPI, self).__init__()

    def get(self):
        return jsonify(users.keys())

api.add_resource(UserListAPI, '/v1/users', endpoint='users')

class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user_id', type=str, location='json')
        super(UserAPI, self).__init__()

    def post(self, user_id):
        args = self.reqparse.parse_args()
        if user_id in users:
            abort(409)
        users[user_id] = set()
        return jsonify( { 'user': user_id } )

    def delete(self, user_id):
        args = self.reqparse.parse_args()
        if user_id not in users:
            abort(404)
        del users[user_id]
        return jsonify( { 'user': user_id } )

api.add_resource(UserAPI, '/v1/users/<string:user_id>', endpoint='user')

class UserLikeListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('page', type=int, required=False, location='json')
        self.reqparse.add_argument('n_results', type=int, required=False, location='json')
        super(UserListAPI, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        if user_id not in users:
            abort(404)
        return jsonify(list(users[user_id]))

api.add_resource(UserLikeListAPI, '/v1/users/<string:user_id>/likes', endpoint='userlikes')

class UserLikeAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user_id', type=str, required=True, location='json')
        self.reqparse.add_argument('like_id', type=str, location='json')
        super(UserLikeAPI, self).__init__()

    def post(self, user_id, like_id):
        args = self.reqparse.parse_args()
        if user_id not in users:
            abort(404)
        if like_id not in users[user_id]:
            user[user_id].add(like_id)

    def delete(self, user_id, like_id):
        args = self.reqparse.parse_args()
        if user_id not in users:
            abort(404)
        if like_id in users[user_id]:
            user[user_id].remove(like_id)


api.add_resource(UserLikeAPI, '/v1/users/<string:user_id>/likes/<string:like_id>', endpoint='userlike')


# class ItemAPI(Resource):
#     def get(self, id):
#         pass
#
#     def put(self, id):
#         pass
#
#     def delete(self, id):
#         pass
#
# api.add_resource(UserAPI, '/v1/users/<int:id>', endpoint='user')

if __name__ == '__main__':
    app.run(debug = True)
