#
# spec file for package odr-audioenc and subpackage toolame-dab-odr
#
# Copyright (c) 2016 - 2019 Radio Bern RaBe
#                           http://www.rabe.ch
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public 
# License as published  by the Free Software Foundation, version
# 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License  along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#
# Please submit enhancements, bugfixes or comments via GitHub:
# https://github.com/radiorabe/centos-rpm-odr-audioenc
#

# Important note regarding version and release bumps:
# Do not use rpmdev-bumpspec to bump this Spec file, as it can't handle
# the *_release macros used below. Bump the version and release numbers
# manually by adapting the main_version, main_release, libtoolame_dab_version
# and libtoolame_dab_release macros instead.

# Name of the GitHub repository
%define reponame ODR-AudioEnc

# Names and versions of the (sub)packages
# See https://www.redhat.com/archives/rpm-list/2000-October/msg00216.html
%define main_name odr-audioenc
%define main_version 2.4.1
%define main_release 1%{?dist}

%define toolame_dab_name toolame-dab-odr
# Version relates to libtoolame-dab/HISTORY
%define libtoolame_dab_version 0.2l.odr
%define libtoolame_dab_release 5%{?dist}
%define libtoolame_dab_license LGPLv2+

%define service_user odr-audioenc
%define service_group odr

# Conditional build support
# add --without alsa option, i.e. enable alsa by default
%bcond_without alsa
# add --with jack option, i.e. disable jack by default
%bcond_with jack
# add --with vlc option, i.e. disable vlc by default
%bcond_with vlc

Name:           %{main_name}
Version:        %{main_version}
Release:        %{main_release}
Summary:        DAB and DAB+ audio encoder 

License:        ASL 2.0
URL:            https://github.com/Opendigitalradio/%{reponame}
Source0:        https://github.com/Opendigitalradio/%{reponame}/archive/v%{main_version}.tar.gz#/%{main_name}-%{main_version}.tar.gz
Source1:        %{main_name}@.service


%{?systemd_requires}

BuildRequires:  chrpath
BuildRequires:  fdk-aac-dabplus-odr-devel
BuildRequires:  libtool
BuildRequires:  systemd
BuildRequires:  zeromq-devel

%if %{with alsa}
BuildRequires:  alsa-lib-devel
%endif

%if %{with jack}
BuildRequires:  jack-audio-connection-kit-devel
%endif

%if %{with vlc}
BuildRequires:  vlc-devel
%endif

%description
This package contains a DAB and DAB+ encoder that integrates into the
ODR-mmbTools.
The DAB encoder is based on toolame. The DAB+ encoder uses a modified library
of the Fraunhofer FDK AAC code from Android, patched for 960-transform to do
DAB+ broadcast encoding.
The main tool is the odr-audioenc encoder, which can read audio from a file
(raw or wav), from an ALSA source, from JACK or using libVLC, and encode to a
file, a pipe, or to a ZeroMQ output compatible with ODR-DabMux.


%package -n     %{toolame_dab_name}
Version:        %{libtoolame_dab_version}
Release:        %{libtoolame_dab_release}
Summary:        Opendigitalradio's fork of tooLAME
License:        %{libtoolame_dab_license}

%description -n %{toolame_dab_name}
tooLAME is an optimized Mpeg Audio 1/2 Layer 2 encoder. It is based heavily on
- the ISO dist10 code - improvement to algorithms as part of the LAME project,
in form of a library to be used with the encoder for the ODR-mmbTools


%package -n     %{toolame_dab_name}-devel
Version:        %{libtoolame_dab_version}
Release:        %{libtoolame_dab_release}
Summary:        Development files for %{toolame_dab_name}
License:        %{libtoolame_dab_license}
Requires:       %{toolame_dab_name}%{?_isa} = %{libtoolame_dab_version}-%{release}

%description -n %{toolame_dab_name}-devel
The %{toolame_dab_name}-devel package contains libraries and header files for
developing applications that use %{toolame_dab_name}.


%prep
%setup -q -n %{reponame}-%{main_version}


%build
autoreconf -fi
%configure --disable-static \
           %{?with_alsa:--enable-alsa} \
           %{?with_jack:--enable-jack} \
           %{?with_vlc:--enable-vlc}
           
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
%make_install
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

# Remove Rpath to get rid of hardcoded library paths
# and pass the check-rpaths tests:
# ERROR   0002: file '/usr/bin/dabplus-enc' contains an invalid rpath
#
# Unfortunately, passing --disable-rpath to configure is not supported,
# that's why chrpath is used. This should be fixed within the buildsystem
# someday.
chrpath --delete $RPM_BUILD_ROOT%{_bindir}/odr-audioenc

# Install the systemd service unit
install -d %{buildroot}/%{_unitdir}
install -m 644 %{SOURCE1} %{buildroot}/%{_unitdir}


%pre 
getent group %{service_group} >/dev/null || groupadd -r %{service_group}
getent passwd %{service_user} >/dev/null || \
    useradd -r -g %{service_group} -G audio -d /dev/null -m -s /sbin/nologin \
    -c "ODR tools system user account" %{service_user}
exit 0


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc ChangeLog README.md
%{_bindir}/*
%{_unitdir}/%{name}@.service


%files -n %{toolame_dab_name}
%{_libdir}/libtoolame-dab.so.*

%files -n %{toolame_dab_name}-devel
%doc libtoolame-dab/HISTORY libtoolame-dab/README.md
%{_includedir}/libtoolame-dab/*
%{_libdir}/libtoolame-dab.so


%changelog
* Tue Dec 24 2019 Christian Affolter <c.affolter@purplehaze.ch> - 2.4.1-1
- Version bump to 2.4.1 

* Sat Oct 27 2018 Christian Affolter <c.affolter@purplehaze.ch> - 2.3.1-1
- Version bump to 2.3.1

* Sat Nov 18 2017 Christian Affolter <c.affolter@purplehaze.ch> - 2.2.0-1
- Version bump to 2.2.0

* Thu Aug 24 2017 Christian Affolter <c.affolter@purplehaze.ch> - 2.1.0-2
- Adding a systemd service unit template for starting odr-audioenc
- Added a dedicated system user/group

* Tue Aug 22 2017 Christian Affolter <c.affolter@purplehaze.ch> - 2.1.0-1
- Version bump to 2.1.0
- Support for independent main and sub-package release macros
- Removing obsolet libfdk-aac-dabplus-odr sub-package

* Fri Jan 27 2017 Christian Affolter <c.affolter@purplehaze.ch> - 2.0.1-1
- Version bump to 2.0.1

* Sat Sep 24 2016 Christian Affolter <c.affolter@purplehaze.ch> - 2.0.0-1
- Initial release

