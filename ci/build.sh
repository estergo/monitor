#!/bin/bash

set -e

export PATH=$PATH:/usr/local/bin

docker image build -f Dockerfile -t docker-registry.ordernet.co.il:5000/monitor:dev .
docker push docker-registry.ordernet.co.il:5000/monitor:dev