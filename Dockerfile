FROM alpine:3.7
MAINTAINER Martin Borho <martin@borho.net>

## Install packages required
RUN apk update && apk add --no-cache python3 git && \
    apk add --no-cache --virtual=build-dependencies wget ca-certificates && \
    wget "https://bootstrap.pypa.io/get-pip.py" -O /dev/stdout | python3 && \
    apk del build-dependencies && rm -rf /var/cache/apk/*

# Create a mount point
VOLUME ["/src"]

# Copy requirements.txt first will avoid cache invalidation
COPY requirements.txt /tmp/requirements.txt

# Install python dependencies
RUN pip3 install -r /tmp/requirements.txt && pip3 install awscli

# Copy the sources into the image
COPY . /src
WORKDIR /src

RUN python3 setup.py install
RUN mkdir -p /data/gitlab && mkdir /data/github && \
    chown -R nobody.nobody /data/gitlab && \
    chown -R nobody.nobody /data/github

# Run the container as 'www-data'
USER nobody

# Add the default config file for pypicloud
CMD [ "/bin/sh", "/src/run_ecs.sh" ]
