FROM python:2.7
RUN apt-get update && apt-get install -y swig
RUN apt-get install -y --no-install-recommends \
  git-core \
  python \
  python-dev \
  "$virtualenv" \
  gcc \
  swig \
  dialog \
  libaugeas0 \
  libssl-dev \
  libffi-dev \
  ca-certificates \
  dpkg-dev
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
