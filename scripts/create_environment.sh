#!/usr/bin/env bash

set -e

: "${DB_ROOT_PASSWORD?Need to set DB_ROOT_PASSWORD}"
: "${DB_USER?Need to set DB_USER}"
: "${DB_PASSWORD?Need to set DB_PASSWORD}"
: "${DB_PORT?Need to set DB_PORT}"

export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Run mysql docker container
docker rm -f skale-mysql || true
docker run -d --restart=always --name skale-mysql -e MYSQL_ROOT_PASSWORD=$DB_ROOT_PASSWORD -e MYSQL_DATABASE=db_skale -e MYSQL_USER=$DB_USER -e MYSQL_PASSWORD=$DB_PASSWORD -v ${DIR}/init.sql:/docker-entrypoint-initdb.d/init.sql -p ${DB_PORT}:3306  mysql/mysql-server:5.7

# Prepare directories
sudo mkdir -p /skale_vol/contracts_info
sudo chown -R $USER:$USER /skale_vol
sudo mkdir -p /skale_node_data
sudo chown -R $USER:$USER /skale_node_data


bash ${DIR}/deploy_SM.sh
