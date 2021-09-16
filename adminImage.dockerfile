FROM python:3

RUN mkdir -p /opt/src/voting
WORKDIR /opt/src/voting

COPY voting/roleCheck.py ./roleCheck.py
COPY voting/adminApplication.py ./adminApplication.py
COPY voting/configurationVoting.py ./configurationVoting.py
COPY voting/modelsVoting.py ./modelsVoting.py
COPY voting/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./adminApplication.py"]