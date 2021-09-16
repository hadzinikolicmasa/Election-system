import datetime;
import io;
from modelsVoting import database;
from flask import Flask,request, Response,jsonify;
from configurationVoting import Configuration;
from email.utils import parseaddr;
import json,re,math,csv;
from sqlalchemy import and_;
from redis import Redis;
from roleCheck import roleCheck;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;

application = Flask(__name__);
application.config.from_object(Configuration);
jwt = JWTManager ( application );

@application.route ( "/", methods = ["GET"] )
def index():
    return "radi voting station";

@application.route ( "/vote", methods = ["POST"] )
@roleCheck ( role = "zvanicnik" )
def vote():
    try:
        content = request.files["file"].stream.read().decode("utf-8");
    except:
        message = {'message': "Field file is missing."}
        return Response(json.dumps(message), status=400);

    stream = io.StringIO(content);
    reader = csv.reader(stream);

    i=0;
    for row in reader: #guid, redni broj na listicu

            if (len(row) != 2):
                message = {'message': "Incorrect number of values on line "+ str(i) +"."}
                return Response(json.dumps(message), status=400);
            try:
                val2 =  int(row[1]);
                if val2<=0:
                    message = {'message': "Incorrect poll number on line " + str(i) + "."}
                    return Response(json.dumps(message), status=400);
            except ValueError:
                message = {'message': "Incorrect poll number on line " + str(i) + "."}
                return Response(json.dumps(message), status=400);
            i+=1;
    stream = io.StringIO(content);
    reader = csv.reader(stream);
    claims = get_jwt();
    with Redis(host='redis', port=6379) as redis:
            for row in reader:  # guid, redni broj na listicu
                vote=str(row[0]+","+row[1]+"," + claims["jmbg"]);

                redis.rpush("votes", vote);

    return Response(status=200);



if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug=True, host="0.0.0.0", port=5002);