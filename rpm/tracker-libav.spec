Name:       tracker

%define enable_demo 0

Summary:    An object database, tag/metadata database, search tool and indexer
Version:    1.1.4
Release:    1
Group:      Data Management/Content Framework
License:    GPLv2+
URL:        http://ftp.gnome.org/pub/GNOME/sources/tracker/0.10/
Source0:    http://ftp.gnome.org/pub/GNOME/sources/%{name}/0.14/%{name}-%{version}.tar.xz
Source1:    tracker-rpmlintrc
Source2:    tracker-store.service
Source3:    tracker-miner-fs.service
Source4:    tracker-extract.service
Requires:   libmediaart >= 0.5.0
Requires:   unzip
Requires:   systemd
Requires:   systemd-user-session-targets
Requires:   qt5-plugin-platform-minimal
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
BuildRequires:  pkgconfig(libmediaart-1.0) >= 0.3.0
BuildRequires:  pkgconfig(dbus-glib-1) >= 0.60
BuildRequires:  pkgconfig(enca)
BuildRequires:  pkgconfig(exempi-2.0)
BuildRequires:  pkgconfig(gconf-2.0)
BuildRequires:  pkgconfig(gee-1.0)
BuildRequires:  pkgconfig(glib-2.0) >= 2.38.0
BuildRequires:  pkgconfig(gmime-2.6)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(id3tag)
BuildRequires:  pkgconfig(libexif)
BuildRequires:  pkgconfig(libgsf-1)
BuildRequires:  pkgconfig(libiptcdata)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(ossp-uuid)
BuildRequires:  pkgconfig(poppler-glib)
BuildRequires:  pkgconfig(sqlite3) >= 3.7
BuildRequires:  pkgconfig(taglib)
BuildRequires:  pkgconfig(totem-plparser)
BuildRequires:  pkgconfig(uuid)
#BuildRequires:  pkgconfig(libvala-0.16)
BuildRequires:  pkgconfig(vorbis)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(Qt5Gui)
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavutil)
BuildRequires:  gettext
BuildRequires:  libtool
BuildRequires:  vala-devel >= 0.16
BuildRequires:  giflib-devel
BuildRequires:  intltool
BuildRequires:  libjpeg-devel
BuildRequires:  libtiff-devel >= 3.8.2
BuildRequires:  perl-XML-Parser
BuildRequires:  pygobject2
BuildRequires:  python >= 2.6
BuildRequires:  dbus-python
BuildRequires:  fdupes
BuildRequires:  giflib-devel

%description
Tracker is a powerful desktop-neutral first class object database,
tag/metadata database, search tool and indexer.

It consists of a common object database that allows entities to have an
almost infinte number of properties, metadata (both embedded/harvested as
well as user definable), a comprehensive database of keywords/tags and
links to other entities.

It provides additional features for file based objects including context
linking and audit trails for a file object.

It has the ability to index, store, harvest metadata. retrieve and search
all types of files and other first class objects


%package tests
Summary:    Tests for tracker
Group:      System/X11
Requires:   %{name} = %{version}-%{release}
Requires:   dbus-python
Requires:   pygobject2
Requires:   python >= 2.6

%description tests
Functional tests for tracker to be run once tracker is installed in
the final environment.


%package utils
Summary:    Tracker command line applications to lookup data
Group:      Development/Tools
Requires:   %{name} = %{version}-%{release}

%description utils
Tracker command line applications to lookup data
Included utilities for Tracker are as follows
 tracker-import      Import TTL files.
 tracker-info        Display all information known about an entity.
 tracker-search      Search for entites (files, folders, videos, etc)
 tracker-sparql      Run a SPARQL query against the databases.
 tracker-stats       Get statistics on how many entities are indexed.
 tracker-tag         Add, remove, list tags for entities.


%package devel
Summary:    Development files for %{name}
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}

%description devel
Development files for %{name}.

%prep
%setup -q -n %{name}-%{version}/%{name}


%build
sed -i -e '/gtkdocize/d' autogen.sh
echo "EXTRA_DIST = missing-gtk-doc" > gtk-doc.make
export NOCONFIGURE=1
%autogen
chmod +x tests/functional-tests/create-tests-xml.py

%configure --disable-static \
    --with-compile-warnings=no \
    --disable-gtk-doc \
    --disable-tracker-preferences \
    --disable-tracker-search-bar \
    --disable-tracker-explorer \
    --enable-unit-tests \
    --enable-functional-tests \
    --disable-miner-evolution \
    --disable-miner-flickr \
    --disable-miner-rss \
    --enable-maemo --enable-nemo \
    --enable-guarantee-metadata \
    --with-unicode-support=libicu \
    --disable-tracker-needle \
    --enable-libvorbis \
    --enable-tracker-fts \
    --enable-qt \
    --enable-generic-media-extractor=libav \
    --disable-enca \
    --disable-journal \
    --enable-libgif

make %{?jobs:-j%jobs}

%install
rm -rf %{buildroot}

%make_install
mkdir -p %{buildroot}%{_libdir}/systemd/user/
cp -a %{SOURCE2} %{buildroot}%{_libdir}/systemd/user/
mkdir -p %{buildroot}%{_libdir}/systemd/user/
cp -a %{SOURCE3} %{buildroot}%{_libdir}/systemd/user/
cp -a %{SOURCE4} %{buildroot}%{_libdir}/systemd/user/


mkdir -p %{buildroot}%{_libdir}/systemd/user/user-session.target.wants
ln -s ../tracker-store.service %{buildroot}%{_libdir}/systemd/user/user-session.target.wants/
ln -s ../tracker-miner-fs.service %{buildroot}%{_libdir}/systemd/user/user-session.target.wants/
ln -s ../tracker-extract.service %{buildroot}%{_libdir}/systemd/user/user-session.target.wants/

rm -rf %{buildroot}/%{_datadir}/icons/hicolor/
rm -rf %{buildroot}/%{_datadir}/gtk-doc
# this is 160MB of test data, let's create that during rpm install
rm -f %{buildroot}/%{_datadir}/tracker-tests/ttl/*


%find_lang %{name}

%fdupes  %{buildroot}/%{_datadir}/

%post
/sbin/ldconfig
glib-compile-schemas   /usr/share/glib-2.0/schemas/
if [ "$1" -ge 1 ]; then
systemctl-user daemon-reload || :
systemctl-user restart tracker-store.service tracker-miner-fs.service tracker-extract.service || :
fi


%postun
/sbin/ldconfig
glib-compile-schemas   /usr/share/glib-2.0/schemas/
if [ "$1" -eq 0 ]; then
systemctl-user stop tracker-miner-fs.service tracker-store.service tracker-extract.service || :
systemctl-user daemon-reload || :
fi


%preun tests
# created during post install
rm -f /usr/share/tracker-tests/ttl/*
rm -f /usr/share/tracker-tests/source-data.pkl


%post tests
# this creates ~160MB of test data for the auto tests
cd /usr/share/tracker-tests/
/opt/tests/tracker/bin/generate /opt/tests/tracker/bin/max.cfg


%files -f %{name}.lang
%defattr(-,root,root,-)
%defattr(-, root, root, -)
%{_bindir}/tracker-control
%{_datadir}/dbus-1/services/*
%{_datadir}/man/man1/*
%{_datadir}/tracker/*.xml
%{_datadir}/tracker/languages/*
%{_datadir}/tracker/miners/*
%{_datadir}/tracker/ontologies/*
%{_datadir}/vala/vapi/*
%{_datadir}/tracker/extract-rules/*
%{_datadir}/glib-2.0/schemas/*.xml
%{_libdir}/libtracker-miner-*.so*
%{_libdir}/libtracker-sparql-*.so*
%{_libdir}/libtracker-control-*.so*
%{_libdir}/tracker-*/*.so*
%{_libdir}/tracker-*/extract-modules/*.so*
%{_libdir}/tracker-*/writeback-modules/*.so*
%{_libexecdir}/tracker-extract
%{_libexecdir}/tracker-miner-fs
%{_libexecdir}/tracker-store
%{_libexecdir}/tracker-writeback
%{_libexecdir}/tracker-miner-apps
%{_libexecdir}/tracker-miner-user-guides
%config %{_sysconfdir}/xdg/autostart/tracker-miner-fs.desktop
%config %{_sysconfdir}/xdg/autostart/tracker-store.desktop
%config %{_sysconfdir}/xdg/autostart/tracker-extract.desktop
%config %{_sysconfdir}/xdg/autostart/tracker-miner-apps.desktop
%config %{_sysconfdir}/xdg/autostart/tracker-miner-user-guides.desktop
%{_libdir}/systemd/user/tracker-miner-fs.service
%{_libdir}/systemd/user/tracker-store.service
%{_libdir}/systemd/user/tracker-extract.service
%{_libdir}/systemd/user/user-session.target.wants/tracker-miner-fs.service
%{_libdir}/systemd/user/user-session.target.wants/tracker-store.service
%{_libdir}/systemd/user/user-session.target.wants/tracker-extract.service


%files tests
%defattr(-,root,root,-)
%{_datadir}/tracker-tests/*
#%{_sysconfdir}/dconf/profile/trackertest
/opt/tests/tracker/bin/*


%files utils
%defattr(-,root,root,-)
%{_bindir}/tracker-import
%{_bindir}/tracker-info
%{_bindir}/tracker-search
%{_bindir}/tracker-sparql
%{_bindir}/tracker-stats
%{_bindir}/tracker-tag


%files devel
%defattr(-,root,root,-)
%{_includedir}/tracker-*/libtracker-miner/*.h
%{_includedir}/tracker-*/libtracker-sparql/*.h
%{_includedir}/tracker-*/libtracker-control/*.h
%{_libdir}/pkgconfig/tracker-*.pc
