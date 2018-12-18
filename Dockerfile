FROM python:3.7.1-alpine

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

ARG PIP_INDEX_URL

RUN pip3 install -U setuptools
RUN python -m pip install --upgrade pip

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt --index-url=${PIP_INDEX_URL}

COPY . /usr/src/app

ENV PORT 8080
EXPOSE 8080

# # Run as non-root
RUN chmod -R 775 /usr/src
RUN addgroup -g 1001 -S appuser && adduser -u 1001 -S appuser -G appuser
RUN chown -R appuser:appuser /usr/src/app
USER appuser

ENTRYPOINT ["python3"]

CMD ["/usr/src/app/app.py"]
