FROM python:latest

WORKDIR /home

RUN pip install virtualenvwrapper

RUN virtualenv ./py1

RUN /bin/bash -c 'source ./py1/bin/activate;\
    pip install django;\
    pip install mysqlclient;\
    django-admin startproject myproject'

CMD ["bash"]