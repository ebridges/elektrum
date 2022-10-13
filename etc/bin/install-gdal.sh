#!/bin/sh

# https://gist.github.com/rastermanden/ac171ff6818b038ac549fd92315b5de1

venv=${1}

source "${venv}/bin/activate"

gdal_version='2.4.1'
prefix='/usr'
outputfile="gdal-${gdal_version}.tar.gz"

cd /tmp

if ! [ -f ${outputfile} ];
then
  curl -L "http://download.osgeo.org/gdal/${gdal_version}/gdal-${gdal_version}.tar.gz" -o ${outputfile}
fi

tar zxf ${outputfile}

cd gdal-${gdal_version}

export PATH="${prefix}/bin:$PATH"
export C_INCLUDE_PATH="${prefix}/include:$C_INCLUDE_PATH"
export LIBRARY_PATH="${prefix}/lib:$LIBRARY_PATH"
export LD_LIBRARY_PATH="${prefix}/lib:$LD_LIBRARY_PATH"

./configure --prefix=${prefix} --with-python
make -j4
make install
ldconfig
pip3 install GDAL
