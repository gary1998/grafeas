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
  python3-dev
RUN pip3 install -U setuptools
RUN python -m pip install --upgrade pip
COPY requirements.txt /usr/src/app/
RUN pip3 install -r requirements.txt
COPY . /usr/src/app
EXPOSE 8080
ENTRYPOINT ["python3"]
CMD ["/usr/src/app/app.py"]
