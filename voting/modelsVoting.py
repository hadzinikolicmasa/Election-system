from flask_sqlalchemy import SQLAlchemy;

database=SQLAlchemy();

class ElectionParticipant(database.Model):
    __tablename__ = "electionparticipant";

    id = database.Column(database.Integer, primary_key=True);
    participantId = database.Column(database.Integer, database.ForeignKey("participants.id"), nullable=False);
    electionId = database.Column(database.Integer, database.ForeignKey("elections.id"), nullable=False);
    pollnumber=database.Column(database.Integer, nullable=False );
    number_votes=database.Column(database.Integer, nullable=False );


class Participants(database.Model):
    __tablename__="participants";

    id=database.Column(database.Integer, primary_key=True);
    name=database.Column(database.String(256), nullable=False);
    individual=database.Column(database.Boolean, nullable=False);

    elections = database.relationship("Elections", secondary=ElectionParticipant.__table__, back_populates="participants");

    def __repr__ ( self ):
        return self.name;


class Elections(database.Model):
    __tablename__ = "elections";

    id=database.Column(database.Integer, primary_key=True);
    start=database.Column(database.DateTime, nullable=False);
    end=database.Column(database.DateTime, nullable=False);
    individual=database.Column(database.Boolean, nullable=False);

    participants = database.relationship ( "Participants", secondary = ElectionParticipant.__table__, back_populates = "elections" );

class Voters(database.Model):
    __tablename__ = "voters";

    id_paper=database.Column(database.String(256), primary_key=True);
    id_election=database.Column(database.Integer, primary_key=True);

class InvalidVotes(database.Model):
    __tablename__ = "invalidvotes";

    id=database.Column(database.Integer, primary_key=True);
    electionOfficialJMBG= database.Column(database.String(13), nullable=False);
    ballotGuid=database.Column(database.String(256), nullable=False);
    pollnumber=database.Column(database.Integer, nullable=False );
    reason=database.Column(database.String(256), nullable=False);
    electionId = database.Column(database.Integer, database.ForeignKey("elections.id"), nullable=False);




