FROM python:3

RUN mkdir -p /opt/src/voting
WORKDIR /opt/src/voting

COPY voting/daemon.py ./daemon.py
COPY voting/votes.csv ./votes.csv
COPY voting/configurationVoting.py ./configurationVoting.py
COPY voting/modelsVoting.py ./modelsVoting.py
COPY voting/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./daemon.py"]