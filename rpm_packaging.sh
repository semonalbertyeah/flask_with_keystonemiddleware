#!/bin/bash

# set exit on error
set -e

ver="0.1.0"
name="kapp"
release="1"

echo "final package"
echo ${name}-${ver}-${release}.noarch.rpm

# prepare the source code
echo ''
echo '==== copy source code ===='
mkdir -p tmp/${name}/
mkdir -p tmp/dist/
cp -r kapp/ kapp_manage kapp.service setup.py etc/ MANIFEST.in tmp/${name}/
cp ${name}.spec tmp/
cd tmp/

# prepare tar ball
echo ''
echo '==== create tar ball ===='
tar -cvf ${name}.tar.gz ${name}/

# build rpm
echo ''
echo '==== rpmbuild ===='
mkdir -p ~/rpmbuild/BUILD/ ~/rpmbuild/BUILDROOT/ ~/rpmbuild/RPMS/ ~/rpmbuild/SOURCES/ ~/rpmbuild/SPECS/ ~/rpmbuild/SRPMS/
mv ${name}.tar.gz ~/rpmbuild/SOURCES/
mv ${name}.spec ~/rpmbuild/SPECS/
rpmbuild -bb ~/rpmbuild/SPECS/${name}.spec

mv ~/rpmbuild/RPMS/noarch/${name}-${ver}-${release}.noarch.rpm dist
