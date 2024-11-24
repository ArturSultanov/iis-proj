FROM python:3.12

WORKDIR /work

COPY ./requirements.txt /work/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /work/requirements.txt

COPY ./app /work/app
COPY ./mysql /work/mysql
COPY ./static /work/static
COPY ./templates /work/templates
COPY ./main.py /work/main.py

CMD ["python", "main.py"]
