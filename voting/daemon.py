import datetime;
from flask import Flask,request, Response,jsonify;
from modelsVoting import database, Participants, Elections,ElectionParticipant,InvalidVotes,Voters;
from configurationVoting import Configuration;
from email.utils import parseaddr;
import json,re,math,csv;
from sqlalchemy import and_;
from redis import Redis;
from datetime import datetime;
from datetime import date;
import pytz;


application = Flask ( __name__ );
application.config.from_object ( Configuration );


database.init_app ( application );

with application.app_context ( ) as context:
    with Redis(host='redis', port=6379) as redis:
       k=0;
       while (1):


            while not redis.lrange("votes", 0, -1):  # ceka na glasove
                continue;
            elections=Elections.query.all();
            active = False;
            id = 0;

            for election in elections:

                tz = pytz.timezone('Europe/Vienna');
                now = datetime.now(tz=tz);



                if (election.start.replace(tzinfo=None) < now.replace(tzinfo=None) and election.end.replace(tzinfo=None) > now.replace(tzinfo=None)):
                    active = True;
                    id = election.id;
                    break;

            if (active == True):

                vote = str(redis.lpop("votes"));
                vote=vote.split(",")
                guid = str(vote[0]).split("'")[1];
                poll = int(vote[1]);
                jmbg=str(vote[2]).split("'")[0];


                list = Voters.query.filter(and_(Voters.id_paper == guid, Voters.id_election == id)).first();
                participant_election = ElectionParticipant.query.filter(and_(ElectionParticipant.electionId == id, ElectionParticipant.pollnumber == poll)).first();

                if (list):
                    invalid_vote = InvalidVotes(electionOfficialJMBG=jmbg, ballotGuid=guid, pollnumber=poll,
                                                reason="Duplicate ballot.", electionId=id);
                    database.session.add(invalid_vote);
                    database.session.commit();
                elif (not participant_election):
                    invalid_vote = InvalidVotes(electionOfficialJMBG=jmbg, ballotGuid=guid, pollnumber=poll,
                                                reason="Invalid poll number.", electionId=id);
                    database.session.add(invalid_vote);
                    database.session.commit();
                else:

                    participant_election.number_votes += 1;
                    database.session.commit();
                    voter=Voters(id_paper=guid,id_election=id);

                    database.session.add(voter);
                    database.session.commit();

            else:
                vote = redis.lpop("votes");






