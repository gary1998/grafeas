FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install dependencies
RUN apk update \
&& apk add --no-cache \
  ca-certificates \
\
# Install build dependencies
&& apk add --no-cache --virtual .build-deps \
  gcc \
  libffi-dev \
  openssl-dev \
  make \
  musl-dev \
  python3-dev \
  git

RUN pip3 install -U setuptools
RUN python -m pip install --upgrade pip

COPY requirements.txt /usr/src/app/


ARG GHE_ACCESS_TOKEN

RUN mkdir iam_py  \
     && cd iam_py \
     && git init \
     && git pull https://${GHE_ACCESS_TOKEN}@github.ibm.com/jagkuma3/iam_manager_python.git

RUN pip3 install --no-cache-dir -r requirements.txt \
  && pip3 install -e iam_py

COPY . /usr/src/app
EXPOSE 8080
ENTRYPOINT ["python3"]

CMD ["/usr/src/app/app.py"]