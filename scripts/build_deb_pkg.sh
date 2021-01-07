#! /bin/sh

SW_NAME=spacelab-decoder
PKT_VERSION=0.3.0-0
DIST=ubuntu
DIST_VERSION=20.04
PKT_NAME=${SW_NAME}_${PKT_VERSION}_${DIST}${DIST_VERSION}

SW_ICON=../spacelab-decoder/icon/spacelab_decoder_256x256.png
SW_BIN=../build/spacelab-decoder

mkdir /tmp/${PKT_NAME}
mkdir /tmp/${PKT_NAME}/DEBIAN
mkdir /tmp/${PKT_NAME}/usr
mkdir /tmp/${PKT_NAME}/usr/bin
mkdir /tmp/${PKT_NAME}/usr/lib64
mkdir /tmp/${PKT_NAME}/usr/share
mkdir /tmp/${PKT_NAME}/usr/share/applications
mkdir /tmp/${PKT_NAME}/usr/share/icons

cat > /tmp/${PKT_NAME}/DEBIAN/control << 'EOF'
Package: spacelab-decoder
Version: 0.3.0-0
Section: base
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.9.2), python3-scipy (>= 1.3.3), python3-zmq (>= 18.1.1), python3-gi (>= 3.36.0), gnuradio (>= 3.8.1)
Maintainer: Gabriel Mariano Marcelino <gabriel.mm8@gmail.com>
Description: SpaceLab Packet Decoder is a software to decode audio records from the satellites of SpaceLab.
EOF

cat > /tmp/${PKT_NAME}/usr/share/applications/${SW_NAME}.desktop << 'EOF'
[Desktop Entry]
Type=Application
Encoding=UTF-8
Name=SpaceLab Decoder
Comment=Audio file decoder of the SpaceLab satellites
Icon=/usr/share/icons/spacelab_decoder_256x256.png
Exec=/usr/bin/spacelab-decoder
Terminal=false
Categories=HamRadio
EOF

cp ${SW_ICON} /tmp/${PKT_NAME}/usr/share/icons/${SW_NAME}.png
cp ${SW_BIN} /tmp/${PKT_NAME}/usr/bin/${SW_NAME}
cp ../build/*.so /tmp/${PKT_NAME}/usr/lib64/
cp -r ../spacelab-decoder /tmp/${PKT_NAME}/usr/share/

dpkg-deb --build /tmp/$PKT_NAME/

mv /tmp/${PKT_NAME}.deb .

rm -r /tmp/${PKT_NAME}
