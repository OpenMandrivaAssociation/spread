%define pymod 1.5

%define	major 1
%define libname %mklibname spread %{major}
%define develname %mklibname spread -d

Summary:	Multicast Group Communication Framework
Name:		spread
Version:	3.17.4
Release:	%mkrel 3
Group:		System/Servers
License:	BSD-style
URL:		http://www.spread.org/
Source0:	spread-src-%{version}.tar.bz2
Source1:	http://www.zope.org/Members/tim_one/spread/SpreadModule-%{pymod}/SpreadModule-%{pymod}.tar.bz2
Source2:	spread.init
Source3:	spread.sysconfig
Patch0:		spread-3.17.3-soname.diff
Patch1:		spread-src-3.17.3-mdv_config.diff
Patch2:		spread-src-force_man_page_format.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	flex
BuildRequires:	python-devel
BuildRequires:	groff-for-man

%description
Spread is a toolkit that provides a high performance messaging service that is
resilient to faults across external or internal networks. Spread functions as a
unified message bus for distributed applications, and provides highly tuned
application-level multicast and group communication support. Spread services
range from reliable message passing to fully ordered messages with delivery
guarantees, even in case of computer failures and network partitions. Spread is
designed to encapsulate the challenging aspects of asynchronous networks and
enable the construction of scalable distributed applications, allowing
application builders to focus on the differentiating components of their
application.

%package -n	%{libname}
Summary:	Multicast Group Communication Framework library
Group:          System/Libraries

%description -n	%{libname}
Spread is a toolkit that provides a high performance messaging service that is
resilient to faults across external or internal networks. Spread functions as a
unified message bus for distributed applications, and provides highly tuned
application-level multicast and group communication support. Spread services
range from reliable message passing to fully ordered messages with delivery
guarantees, even in case of computer failures and network partitions. Spread is
designed to encapsulate the challenging aspects of asynchronous networks and
enable the construction of scalable distributed applications, allowing
application builders to focus on the differentiating components of their
application.

%package -n	%{develname}
Summary:	Static library and header files for the libevent library
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	lib%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname spread 1 -d}

%description -n	%{develname}
Spread is a toolkit that provides a high performance messaging service that is
resilient to faults across external or internal networks. Spread functions as a
unified message bus for distributed applications, and provides highly tuned
application-level multicast and group communication support. Spread services
range from reliable message passing to fully ordered messages with delivery
guarantees, even in case of computer failures and network partitions. Spread is
designed to encapsulate the challenging aspects of asynchronous networks and
enable the construction of scalable distributed applications, allowing
application builders to focus on the differentiating components of their
application.

This package includes the necessary files to develop systems with Spread.

%package -n	python-spread
Summary:	Python wrapper for Spread client libraries
Group:		Development/Python

%description -n	python-spread
This package contains a simple Python wrapper module for the Spread toolkit.
The wrapper is known to be compatible with Python 2.3 and 2.4. It may work
with earlier Pythons, but this has not been tested.

Spread (www.spread.org) is a group communications package.  You'll need to
download and install it separately.  The Python API has been built and tested
against Spreads 3.16.1 through 3.17.3, although at least Spread 3.17 is
required to use this version of the wrapper. 3.17.3 is recommended.

%prep

%setup -q -n spread-src-%{version} -a1
%patch0 -p0 -b .soname
%patch1 -p0 -b .mdv_config
%patch2 -p1 -b .force_man_page_format

cp %{SOURCE2} spread.init
cp %{SOURCE3} spread.sysconfig

%build

%configure \
    --with-mantype=man \
    --with-pid-dir=/var/run/spread

%make

pushd SpreadModule-%{pymod}
    python setup.py build_ext -I .. -L ..
popd

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%makeinstall_std

install -d %{buildroot}%{_sysconfdir}/{sysconfig,logrotate.d}
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}/var/log/spread
install -d %{buildroot}/var/run/spread

install -m0644 sample.spread.access_ip %{buildroot}%{_sysconfdir}/spread.access_ip
install -m0755 spread.init %{buildroot}%{_initrddir}/spread
install -m0644 spread.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/spread

touch %{buildroot}/var/log/spread/spread.log

pushd SpreadModule-%{pymod}
    python setup.py install --root %{buildroot}
popd

# install log rotation stuff
cat > %{buildroot}%{_sysconfdir}/logrotate.d/spread << EOF
/var/log/spread/spread.log {
    create 644 spread spread
    monthly
    compress
    missingok
    postrotate
	/bin/kill -HUP `cat /var/run/spread/spread.pid 2> /dev/null` 2> /dev/null || true
    endscript
}
EOF

%pre
%_pre_useradd spread /var/run/spread /bin/false

%post
%create_ghostfile /var/log/spread/spread.log spread spread 0644
%_post_service spread

%preun
%_preun_service spread

%postun
%_postun_userdel spread

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CVS_Readme.txt Changelog PORTING Readme.txt Short_Buffer_Handling.txt TODO
%doc license.txt
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/spread.*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/spread
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/spread
%attr(0755,root,root) %{_initrddir}/spread
%{_bindir}/sp*
%{_sbindir}/sp*
%{_mandir}/man1/*
%attr(0755,spread,spread) %dir /var/run/spread
%attr(0755,spread,spread) %dir /var/log/spread
%attr(0644,spread,spread) %ghost /var/log/spread/spread.log

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/lib*.so.*

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/lib*.so
%{_libdir}/lib*.a
%{_includedir}/*
%{_mandir}/man3/*

%files -n python-spread
%defattr(-,root,root)
%doc SpreadModule-%{pymod}/CHANGES SpreadModule-%{pymod}/doc.txt SpreadModule-%{pymod}/LICENSE
%doc SpreadModule-%{pymod}/README SpreadModule-%{pymod}/TODO.txt
%{_libdir}/python*/site-packages/*
