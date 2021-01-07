#! /bin/sh

SW_NAME=spacelab-decoder
SW_VERSION=0.3.0
SPEC_SCRIPT=${SW_NAME}.spec
SW_BIN=../build/spacelab-decoder
SW_ICON=../spacelab-decoder/icon/spacelab_decoder_256x256.png
SW_SRC=../spacelab-decoder

rpmdev-setuptree

cp ${SPEC_SCRIPT} ${HOME}/rpmbuild/SPECS/

OLDPWD=$(pwd)
mkdir /tmp/${SW_NAME}-${SW_VERSION}
mkdir /tmp/${SW_NAME}-${SW_VERSION}/${SW_NAME}
cp ${SW_BIN} /tmp/${SW_NAME}-${SW_VERSION}/${SW_NAME}-exec
cp ../*.so /tmp/${SW_NAME}-${SW_VERSION}/
cp ${SW_ICON} /tmp/${SW_NAME}-${SW_VERSION}/spacelab_decoder_256x256.png
cp -r ${SW_SRC} /tmp/${SW_NAME}-${SW_VERSION}/
cd /tmp/
tar -czvf ${HOME}/rpmbuild/SOURCES/${SW_NAME}.tar.gz ${SW_NAME}-${SW_VERSION}
rm -r /tmp/${SW_NAME}-${SW_VERSION}
cd ${OLDPWD}

rpmbuild -bb ${HOME}/rpmbuild/SPECS/${SPEC_SCRIPT}

find ${HOME}/rpmbuild/RPMS/ -type f -name "${SW_NAME}-${SW_VERSION}*.rpm" -exec cp {} ./ \;
