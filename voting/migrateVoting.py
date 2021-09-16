from flask import Flask;
from configurationVoting import Configuration;
from flask_migrate import Migrate, init, migrate, upgrade;
from modelsVoting import database;
from sqlalchemy_utils import database_exists, create_database;

application = Flask ( __name__ );
application.config.from_object ( Configuration );

migrateObject = Migrate ( application, database );
done=False;
while(done==False):
    try:
        if ( not database_exists ( application.config["SQLALCHEMY_DATABASE_URI"] ) ):
            create_database ( application.config["SQLALCHEMY_DATABASE_URI"] );

        database.init_app ( application );

        with application.app_context ( ) as context:
            init ( );
            migrate ( message = "Production migration" );
            upgrade ( );
            done=True;
    except Exception as error:
        print(error);

