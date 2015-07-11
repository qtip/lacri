FROM python:3.4
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
  swig \
  libssl-dev \
  dpkg-dev
RUN pip install uwsgi
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
EXPOSE 3031
VOLUME ["/static"]
CMD python manage.py migrate && python manage.py collectstatic --clear --noinput && uwsgi --socket 0.0.0.0:3031 --chdir /code --wsgi-file lacriproject/wsgi.py --master --processes 4 --threads 2
