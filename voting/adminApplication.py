import datetime
from flask import Flask,request, Response,jsonify;
from modelsVoting import database, Participants, Elections,ElectionParticipant,InvalidVotes;
from configurationVoting import Configuration;
from email.utils import parseaddr;
import json,re,math;
from sqlalchemy import and_;
import isodate.isodatetime;
from datetime import date;
from roleCheck import roleCheck;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;




application = Flask(__name__);
application.config.from_object(Configuration);
jwt = JWTManager ( application );

@application.route("/", methods = ["GET"])
def index():
    return "RADI ADMIN";


@application.route ( "/createParticipant", methods = ["POST"] )
@roleCheck ( role = "administrator" )
def createParticipant():
    name = request.json.get("name", "");
    name_empty = len(name) == 0;

    if (name_empty):
        message = {'message': "Field name is missing."}
        return Response(json.dumps(message), status=400);

    individual = request.json.get("individual",bool);


    if (individual!=True and individual!=False):
        message = {'message': "Field individual is missing."}
        return Response(json.dumps(message), status=400);

    if(individual==False):
        individual=0;
    else:
        individual=1;

    participant = Participants(name=name, individual=individual);
    database.session.add(participant);
    database.session.commit();

    id = {'id': participant.id};
    return Response(json.dumps(id), status=200);

@application.route ( "/getParticipants", methods = ["GET"] )
@roleCheck ( role = "administrator" )
def getParticipants():
    participans=Participants.query.all();
    list=[];

    for participant in participans:
        one={
            "id":participant.id,
            "name":participant.name,
            "individual":participant.individual
        };
        list.append(one);

    all = {'participants': list};

    return Response(json.dumps(all), status=200);


def validate(str):
    match_iso8601 = re.search('^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):?[0-5][0-9])?$',str);

    if not match_iso8601:
        return False
    else:
        return True

@application.route ( "/createElection", methods = ["POST"] )
@roleCheck ( role = "administrator" )
def createElection():
    start = request.json.get("start", "");
    start_empty = len(start) == 0;

    if (start_empty):
        message = {'message': "Field start is missing."}
        return Response(json.dumps(message), status=400);

    end = request.json.get("end", "");
    end_empty = len(end) == 0;

    if (end_empty):
        message = {'message': "Field end is missing."}
        return Response(json.dumps(message), status=400);

    individual = request.json.get("individual", bool);

    if (individual != True and individual != False):
        message = {'message': "Field individual is missing."}
        return Response(json.dumps(message), status=400);

    participants = request.json.get("participants", "");
    if(participants==""):
        message = {'message': "Field participants is missing."}
        return Response(json.dumps(message), status=400);

    if(validate(start)==False or validate(end)==False):
        message = {'message': "Invalid date and time."}
        return Response(json.dumps(message), status=400);


    start_date = isodate.parse_datetime(start);
    end_date = isodate.parse_datetime(end);

    if(start_date.date()>end_date.date()  or (start_date.date()==end_date.date() and start_date.time()>=end_date.time())):
       message = {'message': "Invalid date and time."}
       return Response(json.dumps(message), status=400);

    elections = Elections.query.all();
    active=False;

    for election in elections:
        if((start_date<=election.start and end_date>election.start)or (start_date>=election.start and start_date<election.end)):
            active=True;
            break;

    if(active==True):
        message = {'message': "Invalid date and time."}
        return Response(json.dumps(message), status=400);

    exist=True;
    for participant in participants:
        p = Participants.query.filter(Participants.id == participant).first();
        if (not p or (p and p.individual!=individual)):
            exist=False;
            break;

    if (exist == False or len(participants)<2):
        message = {'message': "Invalid participants."}
        return Response(json.dumps(message), status=400);

    election = Elections(start=start_date, end=end_date, individual=individual);
    database.session.add(election);
    database.session.commit();

    i=1;
    list=[];

    for participant in participants:
        election_participant=ElectionParticipant(participantId=participant,electionId=election.id,pollnumber=i,number_votes=0);
        database.session.add(election_participant);
        database.session.commit();
        list.append(i);
        i=i+1;

    pollnumbers = {'pollNumbers': list};

    return Response(json.dumps(pollnumbers), status=200);

@application.route ( "/getElections", methods = ["GET"] )
@roleCheck ( role = "administrator" )
def getElections():

    elections=Elections.query.all();
    list_elections = [];

    for election in elections:
        participant_elections = ElectionParticipant.query.filter(ElectionParticipant.electionId ==election.id).all();
        list_participant=[];
        for participant_election in participant_elections:
            participant=Participants.query.filter(Participants.id==participant_election.participantId).first();
            one_participant={
            "id": participant.id,
            "name": participant.name
            };
            list_participant.append(one_participant);
        one_election={
            "id": election.id,
            "start": str(election.start),
            "end": str(election.end),
            "individual": election.individual,
            "participants":list_participant
        };
        list_elections.append(one_election);

    all = {'elections': list_elections};

    return Response(json.dumps(all), status=200);

@application.route ( "/getResults", methods = ["GET"] )
@roleCheck ( role = "administrator" )
def getResults():
    id =request.args.get("id");

    if (id==None):
        message = {'message': "Field id is missing."}
        return Response(json.dumps(message), status=400);

    election=Elections.query.filter(Elections.id== id).first();

    if (not election or id==""):
        message = {'message': "Election does not exist."}
        return Response(json.dumps(message), status=400);

    if(election.start<datetime.datetime.now() and election.end>datetime.datetime.now()):
        message = {'message': "Election is ongoing."}
        return Response(json.dumps(message), status=400);

    participant_elections = ElectionParticipant.query.filter(ElectionParticipant.electionId == election.id).all();

    total = 0; #ukupan broj glasova na tim izborima
    for participant_election in participant_elections:
        total += participant_election.number_votes;


    list = [];
    if(election.individual==True): #predsednicki izbori


        for participant_election in participant_elections:
            participant = Participants.query.filter(Participants.id == participant_election.participantId).first();

            if (total != 0):
                result = (participant_election.number_votes * 100) / total;
            else:
                result = 0;
            one = {
                "pollNumber": participant_election.pollnumber,
                "name": participant.name,
                "result": round(result / 100, 2)
            };
            list.append(one);
    else:
        census_passed = [];
        mandate_list = [];
        quotient_list=[];

        for participant_election in participant_elections:
            if (participant_election.number_votes >= total * 0.05):
                census_passed.append(participant_election);
                mandate_list.append(0);
                quotient_list.append(0);

        mandates=250;
        while mandates>0:
            max=-1;
            winner=-1;
            for i in range(len(quotient_list)):
                quotient_list[i]=census_passed[i].number_votes/(mandate_list[i]+1);

            for i in range(len(quotient_list)):
                if(quotient_list[i]>max):
                    max=quotient_list[i];
                    winner=i;


            mandate_list[winner] += 1;
            mandates-=1;

        for i in  range(len(census_passed)):
            participant = Participants.query.filter(Participants.id == census_passed[i].participantId).first();
            one = {
                    "name": participant.name,
                    "pollNumber": census_passed[i].pollnumber,
                    "result": mandate_list[i]
            };
            list.append(one);
        for participant_election in participant_elections:
            if(participant_election not in census_passed):
                participant = Participants.query.filter(Participants.id == participant_election.participantId).first();
                one = {
                    "name": participant.name,
                    "pollNumber": participant_election.pollnumber,
                    "result": 0
                };
                list.append(one);
    list.sort(key = lambda x:x["pollNumber"])
    votes = [];
    invalidvotes = InvalidVotes.query.filter(InvalidVotes.electionId == id).all();

    for invalidvote in invalidvotes:
        one = {
            "ballotGuid": invalidvote.ballotGuid,
            "electionOfficialJmbg": invalidvote.electionOfficialJMBG,
            "pollNumber": invalidvote.pollnumber,
            'reason': invalidvote.reason
        };
        votes.append(one);

    all = {
        'participants': list,
        'invalidVotes': votes
    };

    return Response(json.dumps(all), status=200);



if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug=True, host="0.0.0.0", port=5001);
