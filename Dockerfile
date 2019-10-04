FROM lambci/lambda:build AS base

RUN yum makecache fast

RUN yum clean all && \
    yum update --assumeyes && \
    yum upgrade --assumeyes

RUN yum install  --assumeyes \
  gcc openssl-devel \
  bzip2-devel \
  libffi-devel \
  wget

RUN wget -qO- https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz | tar xvzf - -C /usr/src
RUN cd /usr/src/Python-3.7.3 && ./configure --enable-optimizations && make install

RUN yum install --assumeyes \
    postgresql \
    postgresql-devel \
    python36-pip

# RUN yum install --assumeyes \
#     yum-utils \
#     epel-release
# RUN yum-config-manager --enable epel && \
#     yum --assumeyes install \
#     automake \
#     blas-devel \
#     gcc \
#     gcc-c++ \
#     gdal-python \
#     geos-devel \
#     hdf5-devel \
#     lapack-devel \
#     libcurl-devel \
#     libyaml-devel \
#     make \
#     postgresql \
#     postgresql-devel \
#     proj-devel \
#     python36

# COPY etc/bin/install-gdal.sh
# RUN /var/task/install-gdal.sh /var/venv

ARG app_home=/home/elektrum
ARG wkdir=$app_home/app/
ARG venv=$app_home/venv/
ARG OPERATING_ENV=production

RUN mkdir -p $wkdir

WORKDIR $wkdir

RUN /bin/rm -rf $venv # https://trello.com/c/Ck6JwOo7
RUN python3 -m venv $venv
COPY pyproject.toml $wkdir
COPY poetry.lock $wkdir
RUN source $venv/bin/activate && \
    pip3 install -U pip && \
    pip3 install 'poetry==0.12.17' && \
    poetry install --no-dev

COPY project $wkdir/project
COPY version.txt $wkdir/project/version.txt
COPY etc/env/${OPERATING_ENV}.env $wkdir/project/.env

RUN echo "source $venv/bin/activate" > $HOME/.profile
RUN echo "alias dj='cd $wkdir/project && python manage.py runserver'" >> $HOME/.profile
ENV PS1="\[$(tput setaf 2)\]zappa\[$(tput sgr0)\]> "
ENV AWS_SECRET_ACCESS_KEY=
ENV AWS_ACCESS_KEY_ID=

EXPOSE 8000

CMD ["bash", "--login"]
