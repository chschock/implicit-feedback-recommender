FORMAT: 1A

# RecApi

## Likes [/likes/user/:user_id/item/:item_id]
Likes are relations between a users and items.

### Create a Like [POST]
Given valid `user_id` and `item_id`, creates a like. If it exists already,
nothing happens.

+ Response 200
+ Response 404:
    Occurs if an id is invalid.

### Delete a Like [DELETE]
Given valid `user_id` and `item_id`, deletes a like. If it doesn't exist,
nothing happens.

+ Response 200
+ Response 404:
    Occurs if an id is invalid.

## Likes bulk [/likes/bulk]

### Create Likes [POST]
Given a list of pairs of representing user_id and item_id, create respective
Likes. For those that exist already, nothing happens.

+ Parameters
    + likes: list of pairs [user_id, item_id]

+ Response 200
+ Response 404:
    Occurs if an id in the list is invalid, or the list doesn't consist of pairs.

## Recommendations [/recommendations/user/:user_id]

### Get recommendations for user [GET]
Get a list of pairs representing items and a score.

+ Response 200
+ Response 404:
    Occurs if an id is invalid.

## Recommendations [/recommendations/user/:user_id]

### Get recommendations for user [GET]
Get a list of pairs representing items and a score.

+ Parameters
    + count: integer >= 0

+ Response 200
    + Body
          [['user423', 0.123], ['user52', 0.122], ['user98', 0.080]]

+ Response 404
    Occurs when `count` parameter or id is invalid

## Maintenance [/maintenance/delete-all-data]

### Delete all data [DELETE]
Deletes all data.

+ Response 200

## Statistics [/statistics]

### Get statistics [GET]
Get some numbers about the current recommender. If no recommender is
currently constructed, active items and active users are not provided.

+ Response 200
    + Body
          {
            'number of items': 1334,
            'number of users: 998',
            'number of active items': 800
            'number of active users': 640
          }
