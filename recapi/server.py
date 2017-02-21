import os
from flask import Flask, jsonify, current_app
from flask_restful import Resource, reqparse, abort
from recapi.extensions import api, db
from recapi.cache import Cache, Like
import re

ID_REGEX = re.compile(r'[a-zA-Z0-9\-_]+')

def abort_if_bad_id(string, hint):
    if ID_REGEX.match(string) is None:
        abort(404, message="'{}' is not valid {}".format(string, hint))

class LikesAPI(Resource):

    def post(self, user_id, item_id):
        abort_if_bad_id(user_id, 'user_id')
        abort_if_bad_id(item_id, 'item_id')
        current_app.cache.add(Like(user_id, item_id))

    def delete(self, user_id, item_id):
        abort_if_bad_id(user_id, 'user_id')
        abort_if_bad_id(item_id, 'item_id')
        current_app.cache.delete(Like(user_id, item_id))

def abort_if_bad_likes(likes):
    for like in likes:
        if not isinstance(like, list):
            abort(404, message="{} is not a list".format(like))
        if not len(like) == 2:
            abort(404, message="{} is not of length 2".format(like))
        abort_if_bad_id(like[0], 'bulk user_id')
        abort_if_bad_id(like[1], 'bulk item_id')

class LikesBulkAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('likes', type=list, required=True, location='json')
        super().__init__()

    def post(self):
        args = self.reqparse.parse_args()
        abort_if_bad_likes(args['likes'])
        likes = [Like(pair[0], pair[1]) for pair in args['likes']]
        current_app.cache.add_many(likes)

def abort_if_bad_count(count):
    if count < 0:
        abort(404, message="{} is negative count".format(count))

class RecommendationsAPI(Resource):
    def __init__(self):
        self.alpha = current_app.config['RECOMMENDER_ALPHA']
        self.beta = current_app.config['RECOMMENDER_BETA']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'count', type=int, required=False, location='args',
            default=current_app.config['RECOMMENDER_DEFAULT_COUNT'])
        super().__init__()

    def get(self, user_id):
        args = self.reqparse.parse_args()
        abort_if_bad_id(user_id, 'user_id')
        abort_if_bad_count(args['count'])
        rmdr = current_app.cache.build_recommender()
        result = rmdr.recommend(
            user_id, args['count'], alpha=self.alpha, beta=self.beta)
        return jsonify(result)

class MaintenanceAPI(Resource):

    def delete(self):
        db.drop_all()
        db.create_all()

def create_app(config_object):
    """
    Factory method to build the app with db, api and cache.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)
    register_api_calls(api)
    api.init_app(app)
    reset_cache(app)
    return app

def register_api_calls(api):
    api.add_resource(LikesAPI,
        '/v1/likes/user/<string:user_id>/item/<string:item_id>', endpoint='likes')
    api.add_resource(LikesBulkAPI,
        '/v1/likes/bulk', endpoint='likes_bulk')
    api.add_resource(RecommendationsAPI,
        '/v1/recommendations/user/<string:user_id>', endpoint='recommendations')
    api.add_resource(MaintenanceAPI,
        '/v1/maintenance/delete-all-data', endpoint='maintenance')

def reset_cache(app):
    """
    Reloads data from the db. In testing condition db content is purged, so it's
    created here.
    """
    with app.app_context():
        if app.config['TESTING']:
            db.create_all()
        current_app.cache = Cache(db)


if __name__ == '__main__':
    app = create_app(config_object=os.environ['APP_SETTINGS'])
    app.logger.info('connected to db %s' % app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(port=app.config['PORT'])
