from flask import Flask;
from configuration import Configuration;
from flask_migrate import Migrate, init, migrate, upgrade;
from models import database, Roles, UserRole, Users;
from sqlalchemy_utils import database_exists, create_database;

application = Flask ( __name__ );
application.config.from_object ( Configuration );

migrateObject = Migrate ( application, database );
done=False;
while (done==False):
    try:
        if ( not database_exists ( application.config["SQLALCHEMY_DATABASE_URI"] ) ):
            create_database ( application.config["SQLALCHEMY_DATABASE_URI"] );

        database.init_app ( application );

        with application.app_context ( ) as context:
            init ( );
            migrate ( message = "Production migration" );
            upgrade ( );

            adminRole = Roles ( name = "administrator" );
            userRole = Roles ( name = "zvanicnik" );

            database.session.add ( adminRole );
            database.session.add ( userRole );
            database.session.commit ( );

            admin = Users (
                    jmbg="0000000000000",
                    forename="admin",
                    surname="admin",
                    email = "admin@admin.com",
                    password = "1"
            );

            database.session.add ( admin );
            database.session.commit ( );

            role=Roles.query.filter(Roles.name=="administrator").first();
            userRole = UserRole(userId=admin.id,roleId=role.id);

            database.session.add(userRole);
            database.session.commit();
            done=True;
    except Exception as error:
        print(error);