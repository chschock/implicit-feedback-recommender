export APP_SETTINGS="recapi.config.ProductionConfig"

# This config doesn't use authentication for the database.
# The user running the app needs to be able to connect to the databases.
# You can setup user/password authentication here:
# export DATABASE_URL="postgresql:///user:secret@database"
export DATABASE_URL="postgresql:///recapi"
export TESTING_DATABASE_URL="postgresql:///recapi_testing"
