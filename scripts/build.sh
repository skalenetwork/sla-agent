#!/usr/bin/env bash

# Auto building of sla/bounty agents docker images

set -e

NAME=sla-agent
REPO_NAME=skalenetwork/$NAME
IMAGE_NAME=$REPO_NAME:$VERSION
LATEST_IMAGE_NAME=$REPO_NAME:latest

: "${VERSION?Need to set VERSION}"

echo "Building $IMAGE_NAME..."
docker build -t $IMAGE_NAME . || exit $?

if [ "$RELEASE" = true ]
then
    docker tag $IMAGE_NAME $LATEST_IMAGE_NAME
fi

echo "========================================================================================="
echo "Built $IMAGE_NAME"
