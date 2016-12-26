%define name kapp
%define version 0.1.0
%define release 1

Summary: KAPP
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}.tar.gz
License: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: UNKNOWN <UNKNOWN>


%description
To demonstrate how to make flask work with keystone middleware.

########################
# preprocess
########################
%prep
%setup -n %{name}


########################
# build
########################
%build
python setup.py build


########################
# install
########################
%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

mkdir -p %{buildroot}/usr/lib/systemd/system/
install -m 644 %{name}.service %{buildroot}/usr/lib/systemd/system/

mkdir -p %{buildroot}/etc/kapp/
install -m 644 etc/kapp/* %{buildroot}/etc/kapp/


########################
# clean after rpmbuild
########################
%clean
rm -rf $RPM_BUILD_ROOT


########################
# files
########################
%files -f INSTALLED_FILES
%defattr(-,root,root)

/usr/lib/systemd/system/%{name}.service

%config /etc/kapp/*
