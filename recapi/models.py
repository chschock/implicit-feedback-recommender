from recapi.extensions import db

class DbLike(db.Model):
    __tablename__ = 'likes'

    user_id = db.Column(db.String(), primary_key=True)
    item_id = db.Column(db.String(), primary_key=True)
    rating = db.Column(db.Integer(), default=1)

    def __init__(self, user_id, item_id, rating=1):
        self.user_id = user_id
        self.item_id = item_id
        self.rating = rating

    def __repr__(self):
        return '<{}|{}>'.format(self.user_id, self.item_id)

    @property
    def tuple(self):
        return (self.user_id, self.item_id)
