## About
[![Build Status](https://cloud.drone.io/api/badges/parejadan/bopbot/status.svg)](https://cloud.drone.io/parejadan/bopbot)


## How To

### Setup Sandbox

```bash
# v13.12.0
apt-get install nodejs

# 6.14.5
apt-get install -y npm

# @vue/cli 4.4.4
npm install -g @vue/cli

# start sandbox server
npm install --prefix sandbox
./run_sandbox.sh
```

debug integration tests
```bash
# 1) setup image used for running integration tests
docker run -it -v "$PWD/.:/code/" beepboppygo/bop-chrome

# 2) setup test website for browser to automate against
apt-get update
apt-get install -y nodejs npm
npm install -g @vue/cli
npm install --prefix sandbox

cd code
./run_sandbox.sh&

# 3) install debugging dependencies (base & test packages)
pip3 install -r requirements/debug.txt

# 4) run tests
pytest bopbot/tests/integration_tests -s
```
