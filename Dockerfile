FROM debian:buster AS websub-base
MAINTAINER SURFnet <info@surfnet.nl>

ARG DEBIAN_FRONTEND=noninteractive
ARG RUNLEVEL=1
ENV TERM linux

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections  && \
    echo "deb http://ftp.de.debian.org/debian/ buster-backports main" >> /etc/apt/sources.list  && \
    apt update -y  && \
    apt install -y openssh-server redis python3 python sudo locales python-setuptools \
    python3-virtualenv virtualenv git vim net-tools bash-completion && \
    apt clean -y && apt-get autoremove -y && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*  && \
    update-locale  && \
    systemctl enable ssh.service  && \
    systemctl disable systemd-timesyncd.service  && \
    echo "exit 0" > /usr/sbin/policy-rc.d  && \
    useradd --create-home -s /bin/bash websub  && \
    install -d -o websub -m 0700 /home/websub/.ssh  && \
    echo -n 'websub:websub' | chpasswd  && \
    mkdir -p /etc/sudoers.d && install -b -m 0440 /dev/null /etc/sudoers.d/websub  && \
    echo 'websub ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers.d/websub && \
    /bin/echo -e '#!/bin/sh\ncp /tmp/authorized_keys ~websub/.ssh\nchown websub:websub ~websub/.ssh/authorized_keys' >> /etc/rc.local && \
    chmod 755 /etc/rc.local

RUN git clone https://github.com/mrvanes/pMDQ.git /opt/websub
RUN virtualenv --python=python3 /opt/websub
RUN /opt/websub/bin/pip install --upgrade /opt/websub[celery,redis]

# sshd services in all containers
EXPOSE 22
EXPOSE 80

STOPSIGNAL SIGRTMIN+3

CMD ["/lib/systemd/systemd"]

