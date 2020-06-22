#!/usr/bin/env bash

set -e

: "${ETH_PRIVATE_KEY?Need to set ETH_PRIVATE_KEY}"
: "${MANAGER_TAG?Need to set MANAGER_TAG}"

docker network create testnet || true
# Run ganache
docker rm -f ganache || true
docker run -d --network testnet -p 8545:8545 -p 8546:8546 --name ganache trufflesuite/ganache-cli:v6.8.1-beta.0 \
    --account="0x${ETH_PRIVATE_KEY},100000000000000000000000000" -l 80000000 -b 1

export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Deploy SKALE manager
docker rm -f sm-depoyer || true
docker pull skalenetwork/skale-manager:$MANAGER_TAG
docker run --name sm-depoyer\
    -v $DIR/contracts_data:/usr/src/manager/data \
    --network testnet \
    -e ENDPOINT=http://ganache:8545 \
    -e PRIVATE_KEY=$ETH_PRIVATE_KEY \
    skalenetwork/skale-manager:$MANAGER_TAG \
    npx truffle migrate --network unique

cp $DIR/contracts_data/unique.json /skale_vol/contracts_info/manager.json