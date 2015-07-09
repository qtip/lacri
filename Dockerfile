FROM python:2.7
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
  swig \
  libssl-dev \
  dpkg-dev
RUN pip install uwsgi
ENV PYTHONUNBUFFERED 1
# apparently a bug in the debian package
RUN ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
EXPOSE 3031
CMD uwsgi --socket 0.0.0.0:3031 --chdir /code --plugin python --wsgi-file lacriproject/wsgi.py --master --processes 4 --threads 2 --logto /log/log
