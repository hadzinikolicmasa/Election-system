from flask import Flask,request, Response,jsonify;
from models import database, Users, UserRole,Roles;
from configuration import Configuration;
from email.utils import parseaddr;
import json,re;
from roleCheck import roleCheck;
from sqlalchemy import and_;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;

application = Flask(__name__);
application.config.from_object(Configuration);

@application.route("/", methods = ["GET"])
def index():
    return "RADI";

@application.route("/register",methods=["POST"])
def register():
    jmbg = request.json.get("jmbg", "");
    forename = request.json.get("forename", "");
    surname = request.json.get("surname", "");
    email = request.json.get("email", "");
    password = request.json.get("password", "");

    jmbg_empty = len (jmbg);
    forename_empty = len(forename);
    surname_empty = len(surname);
    email_empty = len(email);
    password_empty = len(password);


    if jmbg_empty==0:
        message = {'message': "Field jmbg is missing."}
        return Response(json.dumps(message),status=400);
    if forename_empty == 0:
        message = {'message': "Field forename is missing."}
        return Response(json.dumps(message),status=400);
    if surname_empty == 0:
        message = {'message': "Field surname is missing."}
        return Response(json.dumps(message),status=400);
    if email_empty == 0:
        message = {'message': "Field email is missing."}
        return Response(json.dumps(message),status=400);
    if password_empty == 0:
        message = {'message': "Field password is missing."}
        return Response(json.dumps(message), status=400);

    jmbg_valid = re.search("^(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[012])[0-9]{3}(7[0-9]|8[0-9]|9[0-9])[0-9]{4}$", jmbg);

    if not jmbg_valid:
        message = {'message': "Invalid jmbg."}
        return Response(json.dumps(message), status=400);

    sum = 0;
    q = 7;
    for i in range(len(jmbg) - 1):
        sum += int(q) * int(jmbg[i]);
        q -= 1;
        if (q == 1):
            q = 7;

    ostatak = sum % 11;
    if ostatak == 0:
        k = 0;
    else:
        k = 11 - ostatak;
    if int(jmbg[12]) != k:
        message = {'message': "Invalid jmbg."}
        return Response(json.dumps(message), status=400);



    email_valid=len(email);

    if email_valid>256:
        message = {'message': "Invalid email."}
        return Response(json.dumps(message), status=400);

    email_valid = re.search("^.+@.+\..{2,}$", email);

    if not email_valid:
        message = {'message': "Invalid email."}
        return Response(json.dumps(message), status=400);


    password_valid=re.search("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,256}$",password);

    if not password_valid:
        message = {'message': "Invalid password."}
        return Response(json.dumps(message), status=400);

    exist = Users.query.filter(Users.email == email).first();

    if (exist):
        message = {'message': "Email already exists."}
        return Response(json.dumps(message), status=400);


    user = Users(jmbg=jmbg, forename=forename, surname=surname, email=email, password=password);
    database.session.add(user);
    database.session.commit();

    role=Roles.query.filter(Roles.name=="zvanicnik").first();

    userRole=UserRole(userId=user.id,roleId=role.id);
    database.session.add(userRole);
    database.session.commit();

    return Response(status=200);




jwt = JWTManager ( application );
@application.route("/login",methods=["POST"])
def login():
    email = request.json.get("email", "");
    password = request.json.get("password", "");

    email_empty = len(email) == 0;
    password_empty = len(password) == 0;

    if (email_empty):
        message = {'message': "Field email is missing."}
        return Response(json.dumps(message), status=400);

    if (password_empty):
        message = {'message': "Field password is missing."}
        return Response(json.dumps(message), status=400);

    email_valid = len(email);

    if email_valid > 256:
        message = {'message': "Invalid email."}
        return Response(json.dumps(message), status=400);

    email_valid = re.search("^.+@.+\..{2,}$", email);

    if not email_valid:
        message = {'message': "Invalid email."}
        return Response(json.dumps(message), status=400);

    user = Users.query.filter(and_(Users.email == email,Users.email == email, Users.password == password)).first();

    if (not user):
        message = {'message': "Invalid credentials."}
        return Response(json.dumps(message), status=400);

    userrole=UserRole.query.filter(UserRole.userId==user.id).first();
    role=Roles.query.filter(Roles.id==userrole.roleId).first();
    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "jmbg":user.jmbg,
        "email":user.email,
        "roles": role.name
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims);
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims);


    return jsonify(accessToken=accessToken   , refreshToken=refreshToken);


@application.route ( "/refresh", methods = ["POST"] )
@jwt_required ( refresh = True )
def refresh ( ):

    identity = get_jwt_identity ( );
    refreshClaims = get_jwt ( );

    additionalClaims = {
            "forename": refreshClaims["forename"],
            "surname": refreshClaims["surname"],
            "jmbg": refreshClaims["jmbg"],
            "email": refreshClaims["email"],
            "roles": refreshClaims["roles"]
    };
    token=create_access_token(identity=identity, additional_claims=additionalClaims);
    message = {'accessToken': token};
    return Response(json.dumps(message), status=200);

@application.route ( "/delete", methods = ["POST"] )
@roleCheck ( role = "administrator" )
def delete():
    email = request.json.get("email", "");
    email_empty = len(email) == 0;

    if (email_empty):
        message = {'message': "Field email is missing."}
        return Response(json.dumps(message), status=400);

    email_valid = len(email);

    if email_valid > 256:
        message = {'message': "Invalid email."}
        return Response(json.dumps(message), status=400);

    email_valid = re.search("^.+@.+\..{2,}$", email);

    if not email_valid:
        message = {'message': "Invalid email."}
        return Response(json.dumps(message), status=400);

    user = Users.query.filter(Users.email == email).first();

    if (not user):
        message = {'message': "Unknown user."}
        return Response(json.dumps(message), status=400);

    role = UserRole.query.filter(UserRole.userId == user.id).first();

    database.session.delete(role);
    database.session.commit();

    database.session.delete(user);
    database.session.commit();

    return Response(status=200);



if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug=True, host="0.0.0.0", port=5000);
