%{?scl:%scl_package python-nose}
%{!?scl:%global pkg_name %{name}}

%global upstream_name nose

# Enable building without docs to avoid a circular dependency between this and python-sphinx
%global with_docs 1

Name:           %{?scl_prefix}python-nose
Version:        1.3.7
Release:        3%{?dist}
Summary:        Discovery-based unittest extension for Python

Group:          Development/Languages
License:        LGPLv2+ and Public Domain
URL:            http://somethingaboutorange.com/mrl/projects/nose/
Source0:        http://pypi.python.org/packages/source/n/nose/nose-%{version}.tar.gz

# Make compatible with coverage 4.1
# https://github.com/nose-devs/nose/pull/1004
Patch0:         python-nose-coverage4.patch
# Fix python 3.5 compat
# https://github.com/nose-devs/nose/pull/983
Patch1:         python-nose-py35.patch
# Fix UnicodeDecodeError with captured output
# https://github.com/nose-devs/nose/pull/988
Patch2:         python-nose-unicode.patch
# Allow docutils to read utf-8 source
Patch3:         python-nose-readunicode.patch
# Fix Python 3.6 compatibility
# Python now returns ModuleNotFoundError instead of the previous ImportError
# https://github.com/nose-devs/nose/pull/1029
Patch4:         python-nose-py36.patch
# Fix documentation generation with the python3 version of sphinx
# https://github.com/nose-devs/nose/issues/481
Patch5: python-nose-py3-sphinx.patch

BuildRoot:      %{_tmppath}/%{pkg_name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  %{?scl_prefix}python-devel
BuildRequires:  %{?scl_prefix}python-setuptools
BuildRequires:  dos2unix
BuildRequires:  %{?scl_prefix}python-coverage >= 3.4-1
Requires:       %{?scl_prefix}python-setuptools

%description
nose extends the test loading and running features of unittest, making
it easier to write, find and run tests.

By default, nose will run tests in files or directories under the
current working directory whose names include "test" or "Test" at a
word boundary (like "test_this" or "functional_test" or "TestClass"
but not "libtest"). Test output is similar to that of unittest, but
also includes captured stdout output from failing tests, for easy
print-style debugging.

These features, and many more, are customizable through the use of
plugins. Plugins included with nose provide support for doctest, code
coverage and profiling, flexible attribute-based test selection,
output capture and more.

%package docs
Summary:        Nose Documentation
Group:          Documentation
%if 0%{?with_docs}
BuildRequires:  %{?scl_prefix}python-sphinx
%endif
Requires:       %{?scl_prefix}python-nose

%description docs
Documentation for Nose

%prep
%setup -q -n %{upstream_name}-%{version}
%patch0 -p1 -b .coverage4
%patch1 -p1 -b .py35
%patch2 -p1 -b .unicode
%patch3 -p1 -b .unicode
%patch4 -p1 -b .py36
%patch5 -p1 -b .py3sphinx

dos2unix examples/attrib_plugin.py

%build
%{?scl:scl enable %{scl} "}
%{__python3} setup.py build
%{?scl:"}

%install
rm -rf %{buildroot}
%{?scl:scl enable %{scl} "}
%{__python3} setup.py install --skip-build --root %{buildroot} \
           --install-data=%{_datadir}
%{?scl:"}

%if 0%{?with_docs}
pushd doc
%{?scl:scl enable %{scl} - << \EOF}
make html
%{?scl:EOF}
rm -rf .build/html/.buildinfo .build/html/_sources
mv .build/html ..
rm -rf .build
popd
%endif # with_docs
cp -a doc reST
rm -rf reST/.static reST/.templates


%check
%{?scl:scl enable %{scl} "}
%{__python3} setup.py build_tests
%{__python3} selftest.py
%{?scl:"}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc AUTHORS CHANGELOG lgpl.txt NEWS README.txt
%{_bindir}/nosetests
%{_bindir}/nosetests-%{python3_version}
%{_mandir}/man1/nosetests.1.gz
%{python3_sitelib}/nose*

%files docs
%defattr(-,root,root,-)
%doc reST examples
%if 0%{?with_docs}
%doc html
%endif # with_docs

%changelog
* Mon Jun 19 2017 Charalampos Stratakis <cstratak@redhat.com> - 1.3.7-3
- Rebuild with docs for rh-python36

* Sat Feb 13 2016 Robert Kuska <rkuska@redhat.com> - 1.3.7-2
- Build with docs

* Sat Feb 13 2016 Robert Kuska <rkuska@redhat.com> - 1.3.7-1
- Update to 1.3.7

* Wed Jan 21 2015 Matej Stuchlik <mstuchli@redhat.com> - 1.3.4-2
- Rebuild with docs

* Wed Jan 21 2015 Matej Stuchlik <mstuchli@redhat.com> - 1.3.4-1
- Update to 1.3.4

* Mon Nov 18 2013 Robert Kuska <rkuska@redhat.com> - 1.3.0-3
- Build with docs

* Mon Nov 18 2013 Robert Kuska <rkuska@redhat.com> - 1.3.0-2
- Bump to avoid release number conflict with rhel-7.0

* Fri Nov 15 2013 Robert Kuska <rkuska@redhat.com> - 1.3.0-1
- Update to 1.3.0

* Mon Jun 10 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1.2.1-6
- Fix all Python 3.3 tests using upstream patches, fixes rhbz#971412.

* Thu May 09 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1.2.1-5
- Fix test failing on Python 3.3.1 using upstream patch.

* Thu May 09 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1.2.1-4
- Rebuild to generate bytecode properly after fixing rhbz#956289

* Wed Jan 23 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1.2.1-3
- Enable building docs.

* Wed Jan 09 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1.2.1-2
- Rebuilt for SCL.

* Wed Sep 12 2012 Toshio Kuratomi <toshio@fedoraproject.org> - 1.2.1-1
- New upsream 1.2.1 that just bumps the version properly

* Mon Sep 10 2012 Toshio Kuratomi <toshio@fedoraproject.org> - 1.2.0-1
- Update to nose-1.2.0.
- Two less python3 test failures than 1.1.2

* Sat Aug  4 2012 David Malcolm <dmalcolm@redhat.com> - 1.1.2-5
- rebuild for https://fedoraproject.org/wiki/Features/Python_3.3
- disable selftests that fail under 3.3

* Fri Aug  3 2012 David Malcolm <dmalcolm@redhat.com> - 1.1.2-4
- remove rhel logic from with_python3 conditional

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Aug 1 2011 Toshio Kuratomi <toshio@fedoraproject.org> - 1.1.2-1
- Upstream bugfix release

* Wed Jul 27 2011 Toshio Kuratomi <toshio@fedoraproject.org> - 1.1.1-1
- Upstream bugfix release

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Dec 26 2010 Toshio Kuratomi <toshio@fedoraproject.org> - 1.0.0-1
- Update to 1.0.0
- Create the docs subpackage for text docs even if we don't create the html docs.
- Make python3 subpackage

* Tue Dec 7 2010 Toshio Kuratomi <toshio@fedoraproject.org> - 0.11.4-2
- Fix FTBFS with newer coverage

* Thu Oct 21 2010 Luke Macken <lmacken@redhat.com> - 0.11.4-1
- Update to 0.11.4 (#3630722)

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 0.11.3-5
- add support for building without docs, to avoid a circular build-time
dependency between this and python-sphinx; disable docs subpackage for now
- add (apparently) missing BR on python-coverage (appears to be needed
for %%check)
- cherrypick upstream compatibility fixes for 2.7

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 0.11.3-4
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Thu May 20 2010 Luke Macken <lmacken@redhat.com> - 0.11.3-3
- Update URL to http://code.google.com/p/python-nose/
- Align description to reflect that in setup.py
- Create a docs subpackage containing HTML & reST documentation
- Thanks to Gareth Armstrong at HP for the patch

* Thu May 06 2010 Luke Macken <lmacken@redhat.com> - 0.11.3-2
- Don't hardcode the python version

* Thu May 06 2010 Luke Macken <lmacken@redhat.com> - 0.11.3-1
- Update to 0.11.3
- Enable the self tests

* Mon Oct 05 2009 Luke Macken <lmacken@redhat.com> - 0.11.1-2
- Include the new nosetests-2.6 script as well

* Mon Oct 05 2009 Luke Macken <lmacken@redhat.com> - 0.11.1-1
- Update to 0.11.1

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.10.4-1
- Update to 0.10.4 to fix 2.6 issues

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.10.3-2
- Rebuild for Python 2.6

* Sat Aug 02 2008 Luke Macken <lmacken@redhat.com> 0.10.3-1
- Update to 0.10.3

* Thu Feb 28 2008 Luke Macken <lmacken@redhat.com> 0.10.1-1
- Update to 0.10.1

* Mon Dec  3 2007 Luke Macken <lmacken@redhat.com> 0.10.0-2
- Add python-setuptools to Requires (Bug #408491)

* Tue Nov 27 2007 Luke Macken <lmacken@redhat.com> 0.10.0-1
- 0.10.0

* Sun Sep  2 2007 Luke Macken <lmacken@redhat.com> 0.10.0-0.3.b1
- Update for python-setuptools changes in rawhide

* Tue Aug 21 2007 Luke Macken <lmacken@redhat.com> 0.10.0-0.2.b1
- 0.10.0b1
- Update license tag to LGPLv2

* Fri Jun 20 2007 Luke Macken <lmacken@redhat.com> 0.10.0-0.1.a2
- 0.10.0a2

* Sat Jun  2 2007 Luke Macken <lmacken@redhat.com> 0.9.3-1
- Latest upstream release
- Remove python-nose-0.9.2-mandir.patch

* Sat Mar  3 2007 Luke Macken <lmacken@redhat.com> 0.9.2-1
- Add nosetests(1) manpage, and python-nose-0.9.2-mandir.patch to put it in
  the correct location.
- 0.9.2

* Sat Dec  9 2006 Luke Macken <lmacken@redhat.com> 0.9.1-2
- Rebuild for python 2.5

* Fri Nov 24 2006 Luke Macken <lmacken@redhat.com> 0.9.1-1
- 0.9.1

* Fri Sep  8 2006 Luke Macken <lmacken@redhat.com> 0.9.0-1
- 0.9.0

* Wed Apr 19 2006 Ignacio Vazquez-Abrams <ivazquez@ivazquez.net> 0.8.7.2-1
- Initial RPM release
