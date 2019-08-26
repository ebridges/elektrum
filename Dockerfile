FROM lambci/lambda:build AS base

RUN yum clean all && \
    yum update --assumeyes && \
    yum upgrade --assumeyes
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

ARG app_home=/home/elektron
ARG wkdir=$app_home/app/
ARG venv=$app_home/zappa-venv
ARG OPERATING_ENV=production

RUN mkdir -p $wkdir

WORKDIR $wkdir

RUN python3 -m venv $venv
COPY pyproject.toml $wkdir
COPY poetry.lock $wkdir
RUN source $venv/bin/activate && \
    pip3 install -U pip && \
    pip3 install 'poetry==0.12.11' && \
    poetry install --no-dev

COPY project $wkdir/project
COPY version.txt $wkdir/project/version.txt
COPY etc/env/${OPERATING_ENV}.env $wkdir/project/.env

RUN echo "source $venv/bin/activate" > $HOME/.profile
RUN echo "alias dj='cd $wkdir/project && python manage.py runserver'" >> $HOME/.profile
ENV PS1="\[$(tput setaf 2)\]zappa\[$(tput sgr0)\]> "
ENV AWS_SECRET_ACCESS_KEY=
ENV AWS_ACCESS_KEY_ID=
ENV ELEKTRON_ENV=${ELEKTRON_ENV}

EXPOSE 8000

CMD ["bash", "--login"]
