#!/usr/bin/env bash

set -e

: "${ETH_PRIVATE_KEY?Need to set ETH_PRIVATE_KEY}"
: "${MANAGER_TAG?Need to set MANAGER_TAG}"

# Run ganache
docker rm -f ganache || true
docker run -d --network host --name ganache trufflesuite/ganache-cli:v6.8.1-beta.0 \
    --account="0x${ETH_PRIVATE_KEY},100000000000000000000000000" -l 80000000 -b 1

export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Deploy SKALE manager
docker pull skalenetwork/skale-manager:$MANAGER_TAG
docker run \
    -v $DIR/contracts_data:/usr/src/manager/data \
    --network host \
    -e ENDPOINT=http://127.0.0.1:8545 \
    -e PRIVATE_KEY=$ETH_PRIVATE_KEY \
    skalenetwork/skale-manager:$MANAGER_TAG \
    npx truffle migrate --network unique

cp $DIR/contracts_data/unique.json /skale_vol/contracts_info/manager.json