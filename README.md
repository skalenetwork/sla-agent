![Test](https://github.com/skalenetwork/sla-agent/workflows/Test/badge.svg)
![Build and publish](https://github.com/skalenetwork/sla-agent/workflows/Build%20and%20publish/badge.svg)
[![codecov](https://codecov.io/gh/skalenetwork/sla-agent/branch/develop/graph/badge.svg)](https://codecov.io/gh/skalenetwork/sla-agent)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4faa45f48f164683bc985648136e74a7)](https://www.codacy.com/gh/skalenetwork/sla-agent?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=skalenetwork/sla-agent&amp;utm_campaign=Badge_Grade)
[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

# SKALE SLA Agent

SKALE SLA Agent is a part of each SKALE Node, and together is part of the SKALE Node Monitoring Service (NMS).

Every SKALE node has a NMS group of N (e.g. 24) other nodes in the network randomly assigned to it. NMS groups regularly audit node downtime and latency at predetermined periods (e.g. five minutes), log these measurements to their local databases, and submit average metrics to the SKALE Manager Contract (SMC) once for every reward period - epoch (e.g. 30 days). Every node is rewarded for its validation efforts, based on results sent by NMS group of this node, at the end of each epoch.

SLA agent runs on every node of SKALE network, periodically requests a list of nodes to monitor from SKALE Manager contract, conducts monitoring of these other nodes (e.g. node downtime, latency, container health), logs these measurements, and sends average metrics per epoch to SMC (once for every epoch).

## An important note about production readiness

SLA Agent is still in active development and therefore should be regarded as alpha software. The development is still subject to security hardening, further testing, and breaking changes. This repository has not yet been reviewed or audited for security.

## Development

### Requirements

Python ≥ 3.6.5

### Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Run tests locally

#### Requirements for tests

You have to change the name of `.env_template` file to `.env` and fill it out with your environment variables.
Then run:

```bash
bash ./scripts/create_environment.sh
```

The script above: 
1) runs MySQL docker container with required database and tables created
2) runs Ganache docker container and deploys SKALE Manager contracts to it 

Then run following script to create and enable a test validator and to make some additional preparations for tests:

```bash
python tests/prepare_validator.py
```

#### Run tests

```bash
py.test -v tests/
```

### Build

For building SLA agent docker image locally:

```bash
docker build -t your-sla-image-name .
```

## Documentation

_in process_

## For more information

-   [SKALE Network Website](https://skale.network)
-   [SKALE Network Twitter](https://twitter.com/SkaleNetwork)
-   [SKALE Network Blog](https://skale.network/blog)
    Learn more about the SKALE community over on [Discord](http://skale.chat).

## Contributing

**If you have any questions please ask our development community on [Discord](https://discord.gg/vvUtWJB).**
[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

## License

[![License](https://img.shields.io/github/license/skalenetwork/sla-agent)](LICENSE)

Copyright (C) 2018-present SKALE Labs
