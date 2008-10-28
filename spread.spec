%define	major 2
%define libname %mklibname spread %{major}
%define develname %mklibname spread -d

Summary:	Multicast Group Communication Framework
Name:		spread
Version:	4.0.0
Release:	%mkrel 1
Group:		System/Servers
License:	BSD-style
URL:		http://www.spread.org/
Source0:	spread-src-%{version}.tar.gz
Source2:	spread.init
Source3:	spread.sysconfig
Patch0:		spread-soname.diff
Patch1:		spread-mdv_config.diff
Patch2:		spread-src-force_man_page_format.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	flex
BuildRequires:	groff-for-man
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
Provides:	%{name}-devel = %{version}-%{release}
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

%prep

%setup -q -n spread-src-%{version}
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

%install
rm -rf %{buildroot}

%makeinstall_std

install -d %{buildroot}%{_sysconfdir}/{sysconfig,logrotate.d}
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}/var/log/spread
install -d %{buildroot}/var/run/spread

install -m0644 docs/sample.spread.access_ip %{buildroot}%{_sysconfdir}/spread.access_ip
install -m0755 spread.init %{buildroot}%{_initrddir}/spread
install -m0644 spread.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/spread

touch %{buildroot}/var/log/spread/spread.log

# install log rotation stuff
cat > %{buildroot}%{_sysconfdir}/logrotate.d/spread << EOF
/var/log/spread/spread.log {
    create 644 spread spread
    monthly
    compress
    missingok
    postrotate
	/bin/kill -HUP \`cat /var/run/spread/spread.pid 2> /dev/null\` 2> /dev/null || true
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

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc license.txt release_announcement_*.txt CVS_Readme.txt Readme.txt
%doc docs/PORTING docs/Short_Buffer_Handling.txt docs/TODO
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/spread.*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/spread
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/spread
%attr(0755,root,root) %{_initrddir}/spread
%{_bindir}/flush_user
%{_bindir}/sp*
%{_sbindir}/sp*
%{_mandir}/man1/*
%attr(0755,spread,spread) %dir /var/run/spread
%attr(0755,spread,spread) %dir /var/log/spread
%attr(0644,spread,spread) %ghost /var/log/spread/spread.log

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/lib*.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/lib*.so
%{_libdir}/lib*.a
%{_includedir}/*
%{_mandir}/man3/*
