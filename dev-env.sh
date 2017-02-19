export APP_SETTINGS="recapi.config.DevelopmentConfig"

# This config doesn't use authentication for the database.
# The user running the app needs to be able to connect to the databases.
export DATABASE_URL="postgresql:///recapi"
export TESTING_DATABASE_URL="postgresql:///recapi_testing"
