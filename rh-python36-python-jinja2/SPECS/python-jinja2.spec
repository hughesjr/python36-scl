%{?scl:%scl_package python-jinja2}
%{!?scl:%global pkg_name %{name}}

# Enable building without docs to avoid a circular dependency between this
# and python-sphinx:
%global with_docs 1

Name:		%{?scl_prefix}python-jinja2
Version:	2.9.6
Release:	2%{?dist}
Summary:	General purpose template engine
Group:		Development/Languages
License:	BSD
URL:		http://jinja.pocoo.org/
Source0:	https://files.pythonhosted.org/packages/source/J/Jinja2/Jinja2-%{version}.tar.gz
BuildRoot:	%{_tmppath}/%{pkg_name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:	noarch
BuildRequires:	%{?scl_prefix}python-devel
BuildRequires:	%{?scl_prefix}python-setuptools
BuildRequires:	%{?scl_prefix}python-markupsafe
%if 0%{?with_docs}
BuildRequires:	%{?scl_prefix}python-sphinx
%endif # with_docs
Requires:	%{?scl_prefix}python-markupsafe

%description
Jinja2 is a template engine written in pure Python.  It provides a
Django inspired non-XML syntax but supports inline expressions and an
optional sandboxed environment.

If you have any exposure to other text-based template languages, such
as Smarty or Django, you should feel right at home with Jinja2. It's
both designer and developer friendly by sticking to Python's
principles and adding functionality useful for templating
environments.

%prep
%setup -q -n Jinja2-%{version}

# cleanup
find . -name '*.pyo' -o -name '*.pyc' -delete

# fix EOL
sed -i 's|\r$||g' LICENSE

%build
%{?scl:scl enable %{scl} "}
%{__python3} setup.py build
%{?scl:"}

# for now, we build docs using Python 2.x and use that for both
# packages.
%if 0%{?with_docs}
%{?scl:scl enable %{scl} "}
make -C docs html
%{?scl:"}
%endif # with_docs

%install
rm -rf %{buildroot}
%{?scl:scl enable %{scl} "}
%{__python3} setup.py install -O1 --skip-build \
	    --root %{buildroot}
%{?scl:"}

# remove hidden file
rm -rf docs/_build/html/.buildinfo

%clean
rm -rf %{buildroot}

%check
%{?scl:scl enable %{scl} "}
%{__python3} setup.py test
%{?scl:"}

%files
%defattr(-,root,root,-)
%doc AUTHORS CHANGES LICENSE
%if 0%{?with_docs}
%doc docs/_build/html
%endif # with_docs
%doc ext
%doc examples
%{python3_sitelib}/*
%exclude %{python3_sitelib}/jinja2/_debugsupport.c

%changelog
* Mon Jun 19 2017 Charalampos Stratakis <cstratak@redhat.com> - 2.9.6-2
- Rebuild with docs

* Fri Jun 16 2017 Charalampos Stratakis <cstratak@redhat.com> - 2.9.6-1
- Update to 2.9.6 for rh-python36

* Sat Feb 13 2016 Robert Kuska <rkuska@redhat.com> - 2.8-2
- Build with docs

* Sat Feb 13 2016 Robert Kuska <rkuska@redhat.com> - 2.8-1
- Update to 2.8

* Wed Jan 21 2015 Matej Stuchlik <mstuchli@redhat.com> - 2.7.3-2
- Rebuild with docs

* Fri Dec 12 2014 Robert Kuska <rkuska@redhat.com> - 2.7.3-1
- Update to 2.7.3

* Tue Jun 24 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 2.6-13
- Rebuild to fix 1102894

* Tue Jun 24 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 2.6-12
- Rebuilt to fix 1102893
Resolves: rhbz#1102893

* Fri May 30 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 2.6-11
- Fix CVE-2014-1402
Resolves: rhbz#1102893

* Mon Nov 18 2013 Robert Kuska <rkuska@redhat.com> - 2.6-11
- Build with docs

* Thu May 09 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 2.6-10
- Remove the extraneous dependency on babel.

* Thu May 09 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 2.6-9
- Rebuild to generate bytecode properly after fixing rhbz#956289

* Wed Jan 23 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 2.6-8
- Rebuilt with docs (now really).

* Wed Oct 17 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 2.6-7
- Rebuilt with docs.

* Wed Sep 19 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 2.6-6
- Rebuilt for SCL.

* Sat Aug 04 2012 David Malcolm <dmalcolm@redhat.com> - 2.6-5
- rebuild for https://fedoraproject.org/wiki/Features/Python_3.3

* Fri Aug  3 2012 David Malcolm <dmalcolm@redhat.com> - 2.6-4
- remove rhel logic from with_python3 conditional

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Jul 25 2011 Thomas Moschny <thomas.moschny@gmx.de> - 2.6-1
- Update to 2.6.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jan 18 2011 Thomas Moschny <thomas.moschny@gmx.de> - 2.5.5-3
- Re-enable html doc generation.
- Remove conditional for F-12 and below.
- Do not silently fail the testsuite for with py3k.

* Mon Nov  1 2010 Michel Salim <salimma@fedoraproject.org> - 2.5.5-2
- Move python3 runtime requirements to python3 subpackage

* Wed Oct 27 2010 Thomas Moschny <thomas.moschny@gmx.de> - 2.5.5-1
- Update to 2.5.5.

* Wed Aug 25 2010 Thomas Moschny <thomas.moschny@gmx.de> - 2.5.2-4
- Revert to previous behavior: fail the build on failed test.
- Rebuild for Python 3.2.

* Wed Aug 25 2010 Dan Horák <dan[at]danny.cz> - 2.5.2-3
- %%ifnarch doesn't work on noarch package so don't fail the build on failed tests

* Wed Aug 25 2010 Dan Horák <dan[at]danny.cz> - 2.5.2-2
- disable the testsuite on s390(x)

* Thu Aug 19 2010 Thomas Moschny <thomas.moschny@gmx.de> - 2.5.2-1
- Update to upstream version 2.5.2.
- Package depends on python-markupsafe and is noarch now.

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 2.5-4
- add explicit build-requirement on python-setuptools
- fix doc disablement for python3 subpackage

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 2.5-3
- support disabling documentation in the build to break a circular build-time
dependency with python-sphinx; disable docs for now

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 2.5-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Tue Jul 13 2010 Thomas Moschny <thomas.moschny@gmx.de> - 2.5-1
- Update to upstream version 2.5.
- Create python3 subpackage. 
- Minor specfile fixes.
- Add examples directory.
- Thanks to Gareth Armstrong for additional hints.

* Wed Apr 21 2010 Thomas Moschny <thomas.moschny@gmx.de> - 2.4.1-1
- Update to 2.4.1.

* Tue Apr 13 2010 Thomas Moschny <thomas.moschny@gmx.de> - 2.4-1
- Update to 2.4.

* Tue Feb 23 2010 Thomas Moschny <thomas.moschny@gmx.de> - 2.3.1-1
- Update to 2.3.1.
- Docs are built using Sphinx now.
- Run the testsuite.

* Sat Sep 19 2009 Thomas Moschny <thomas.moschny@gmx.de> - 2.2.1-1
- Update to 2.2.1, mainly a bugfix release.
- Remove patch no longer needed.
- Remove conditional for FC-8.
- Compilation of speedup module has to be explicitly requested now.

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 10 2009 Thomas Moschny <thomas.moschny@gmx.de> - 2.1.1-1
- Update to 2.1.1 (bugfix release).

* Thu Dec 18 2008 Thomas Moschny <thomas.moschny@gmx.de> - 2.1-1
- Update to 2.1, which fixes a number of bugs.
  See http://jinja.pocoo.org/2/documentation/changelog#version-2-1.

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 2.0-3
- Rebuild for Python 2.6

* Tue Jul 22 2008 Thomas Moschny <thomas.moschny@gmx.de> - 2.0-2
- Use rpm buildroot macro instead of RPM_BUILD_ROOT.

* Sun Jul 20 2008 Thomas Moschny <thomas.moschny@gmx.de> - 2.0-1
- Upstream released 2.0.

* Sun Jun 29 2008 Thomas Moschny <thomas.moschny@gmx.de> - 2.0-0.1.rc1
- Modified specfile from the existing python-jinja package.
