
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Argentina/Buenos_Aires

RUN apt-get update && apt-get install -y \
    gnucobol3 \
    build-essential \
    python3 \
    python3-venv \
    python3-pip \
    postgresql-client \
    python3-psycopg2 \
    python3-curses \
    procps \
    nano \
    vim \
    less \
    git \
    locales \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i 's/# es_AR.UTF-8 UTF-8/es_AR.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen

ENV LANG=es_AR.UTF-8
ENV LC_ALL=es_AR.UTF-8

WORKDIR /opt/ibmi-lab

CMD ["/bin/bash"]

