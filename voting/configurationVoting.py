import os;
databaseUrl = os.environ["DATABASE_URL"];

class Configuration ( ):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/voting";
    REDIS_HOST="localhost";
    JWT_SECRET_KEY = "JWT_SECRET_KEY";


