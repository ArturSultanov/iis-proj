FROM python:3.12

# add mysql server
RUN apt-get update && apt-get install -y mysql-server

# start mysql server
CMD ["mysqld"]

# create database
RUN mysql -u root -e "CREATE DATABASE IF NOT EXISTS iis;"
RUN mysql -u root -e "CREATE USER IF NOT EXISTS 'user'@'%' IDENTIFIED BY 'user';"
RUN mysql -u root -e "GRANT ALL PRIVILEGES ON iis.* TO 'user'@'%';"
RUN mysql -u root -e "FLUSH PRIVILEGES;"


WORKDIR /work

COPY ./requirements.txt /work/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /work/requirements.txt

COPY ./app /work/app
COPY ./mysql /work/mysql
COPY ./static /work/static
COPY ./templates /work/templates
COPY ./main.py /work/main.py

CMD ["python", "main.py"]
