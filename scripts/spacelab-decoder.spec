Name:           spacelab-decoder
Version:        0.3.0
Release:        1%{?dist}
Summary:        SpaceLab packet decoder

License:        GPLv3+
URL:            https://github.com/spacelab-ufsc/spacelab-decoder
Source0:        %{name}.tar.gz

BuildRequires:  python

%description
SpaceLab Packet Decoder is a software to decode audio records from the satellites of SpaceLab.

%global debug_package %{nil}

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/%{_bindir}
install -m 0755 %{name}-exec %{buildroot}/%{_bindir}/%{name}
mkdir -p %{buildroot}/%{_libdir}
cp libngham.so %{buildroot}/%{_libdir}/libngham.so
cp libngham_fsat.so %{buildroot}/%{_libdir}/libngham_fsat.so
mkdir -p %{buildroot}/%{_datadir}/%{name}
cp -r %{name}/ %{buildroot}/%{_datadir}/
mkdir -p %{buildroot}/%{_datadir}/icons
cp spacelab_decoder_256x256.png %{buildroot}/%{_datadir}/icons/spacelab_decoder_256x256.png
mkdir -p %{buildroot}/%{_datadir}/applications
cat > %{buildroot}/%{_datadir}/applications/%{name}.desktop << 'EOF'
[Desktop Entry]
Type=Application
Encoding=UTF-8
Name=SpaceLab Decoder
Comment=SpaceLab packet decoder
Icon=/usr/share/icons/spacelab_decoder_256x256.png
Exec=/usr/bin/spacelab-decoder
Terminal=false
Categories=HamRadio
EOF
xdg-desktop-icon install --novendor spacelab_decoder_256x256.png

%files
%{_bindir}/%{name}
%{_libdir}/libngham.so
%{_libdir}/libngham_fsat.so
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/spacelab_decoder_256x256.png
%{_datadir}/%{name}/

%changelog
* Wed Jan 06 2021 Gabriel Mariano Marcelino <gabriel.mm8@gmail.com> - 0.3.0-1
- First package release
