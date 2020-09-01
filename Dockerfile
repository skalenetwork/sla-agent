FROM ubuntu:18.04

RUN apt-get update && apt-get install -y software-properties-common && \
    apt-get install -y python3.8 libpython3.8-dev python3.8-venv wget git python3.8-distutils && \
    apt-get install -y default-libmysqlclient-dev build-essential iputils-ping

RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.8 get-pip.py && \
    ln -s /usr/bin/python3.7 /usr/local/bin/python3

RUN mkdir /usr/src/sla
WORKDIR /usr/src/sla

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir -r requirements-dev.txt

ENV PYTHONPATH="/usr/src/sla"
CMD [ "python3", "sla_agent.py" ]
