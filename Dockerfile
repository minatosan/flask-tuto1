FROM python:3.8

WORKDIR /flaskblog

ADD . /flaskblog

COPY /flaskblog/requirements.txt ./
ADD flaskblog/requirements.txt $project_dir

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV FLASK_APP /flaskblog/manage.py