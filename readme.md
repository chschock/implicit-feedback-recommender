# Introduction

All shell commands assume you are in the root directory of the app.

# Installation

Setup python 3.5 and pip.
From the root directory of the package execute
```
pip3 install -e ./
```

# Setup database
Install Postgres 9.5 locally. Create two databases, one for production, one
for testing.
```
createdb recapi
createdb recapi_testing
```

Authentication is accomplished by allowing the user running the app to connect
to the databases (refer to pg_hpa.conf). Adapt the settings for development
and production database in the files `dev-env.sh` and `prod-env.sh` if you
chose different names than above or chose a password.

# Configure app

Besides the environment variables, configuration is stored in `config.py`.

Choose your desired server port by setting `PORT`

There are several configuration options for the recommender.

* `RECOMMENDER_DEFAULT_COUNT` is the default number of recommendations
returned by the `recommendations` endpoint
* `RECOMMENDER_ALPHA` is a hyperparameter to relate like based recommendations
to frequency based recommendations
* `RECOMMENDER_BETA` is a factor for the influence of frequent items to the
recommendations
* `RECOMMENDER_MIN_ITEM_FREQUENCY` is the minimum number of times an item has to
appear to become relevant to recommendation
* `RECOMMENDER_MIN_USER_FREQUENCY` is the minimum number of times a user has to
have liked one of the item remaining from the previous condition.


# Run App
Load environment for development
```
source dev-env.sh
```
or production
```
source dev-prod.sh
```

Start app with
```
cd recapi
python3 server.py
```
