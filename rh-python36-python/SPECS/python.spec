# ======================================================
# Conditionals and other variables controlling the build
# ======================================================

# NOTES ON BOOTSTRAPING PYTHON 3.6:
#
# Due to dependency cycle between Python, pip, setuptools and
# wheel caused by the rewheel patch, one has to build in the
# following order:
#
# 1) python3 with with_rewheel set to 0
# 2) python3-setuptools and python3-pip with with_rewheel set to 0
# 3) python3-wheel
# 4) python3-setuptools and python3-pip with with_rewheel set to 1
# 5) python3 with with_rewheel set to 1

%global with_rewheel 0 

%{!?scl:%global pkg_name %{name}}
%{?scl:%scl_package python}
# Turn off default SCL bytecompiling.
%{?scl:%global _turn_off_bytecompile 1}


%global pybasever 3.6

# pybasever without the dot:
%global pyshortver 36

%global pylibdir %{_libdir}/python%{pybasever}
%global dynload_dir %{pylibdir}/lib-dynload

# SOABI is defined in the upstream configure.in from Python-3.2a2 onwards,
# for PEP 3149:
#   http://www.python.org/dev/peps/pep-3149/

# ("configure.in" became "configure.ac" in Python 3.3 onwards, and in
# backports)

# ABIFLAGS, LDVERSION and SOABI are in the upstream Makefile
# With Python 3.3, we lose the "u" suffix due to PEP 393
%global ABIFLAGS_optimized m
%global ABIFLAGS_debug     dm

%global LDVERSION_optimized %{pybasever}%{ABIFLAGS_optimized}
%global LDVERSION_debug     %{pybasever}%{ABIFLAGS_debug}

%global SOABI_optimized cpython-%{pyshortver}%{ABIFLAGS_optimized}-%{_arch}-linux%{_gnu}
%global SOABI_debug     cpython-%{pyshortver}%{ABIFLAGS_debug}-%{_arch}-linux%{_gnu}

# All bytecode files are now in a __pycache__ subdirectory, with a name
# reflecting the version of the bytecode (to permit sharing of python libraries
# between different runtimes)
# See http://www.python.org/dev/peps/pep-3147/
# For example,
#   foo/bar.py
# now has bytecode at:
#   foo/__pycache__/bar.cpython-36.pyc
#   foo/__pycache__/bar.cpython-36.opt-1.pyc
#   foo/__pycache__/bar.cpython-36.opt-2.pyc
%global bytecode_suffixes .cpython-36*.pyc

# Python's configure script defines SOVERSION, and this is used in the Makefile
# to determine INSTSONAME, the name of the libpython DSO:
#   LDLIBRARY='libpython$(VERSION).so'
#   INSTSONAME="$LDLIBRARY".$SOVERSION
# We mirror this here in order to make it easier to add the -gdb.py hooks.
# (if these get out of sync, the payload of the libs subpackage will fail
# and halt the build)
%global py_SOVERSION %{scl}-1.0
%global py_INSTSONAME_optimized libpython%{LDVERSION_optimized}.so.%{py_SOVERSION}
%global py_INSTSONAME_debug     libpython%{LDVERSION_debug}.so.%{py_SOVERSION}

%global with_debug_build 1

%global with_gdb_hooks 1

# some arches don't have valgrind so we need to disable its support on them
%ifnarch s390 %{mips} riscv64
%global with_valgrind 1
%else
%global with_valgrind 0
%endif

%global with_gdbm 1

# Change from yes to no to turn this off
%global with_computed_gotos yes

# Turn this to 0 to turn off the "check" phase:
%global run_selftest_suite 1

# We want to byte-compile the .py files within the packages using the new
# python3 binary.
#
# Unfortunately, rpmbuild's infrastructure requires us to jump through some
# hoops to avoid byte-compiling with the system python 2 version:
#   /usr/lib/rpm/redhat/macros sets up build policy that (amongst other things)
# defines __os_install_post.  In particular, "brp-python-bytecompile" is
# invoked without an argument thus using the wrong version of python
# (/usr/bin/python, rather than the freshly built python), thus leading to
# numerous syntax errors, and incorrect magic numbers in the .pyc files.  We
# thus override __os_install_post to avoid invoking this script:
%global __os_install_post /usr/lib/rpm/brp-%{?scl:scl-}compress %{?_scl_root}\
  %{!?__debug_package:/usr/lib/rpm/brp-strip %{__strip}} \
  /usr/lib/rpm/brp-strip-static-archive %{__strip} \
  /usr/lib/rpm/brp-strip-comment-note %{__strip} %{__objdump} \
  /usr/lib/rpm/redhat/brp-python-hardlink
# to remove the invocation of brp-python-bytecompile, whilst keeping the
# invocation of brp-python-hardlink (since this should still work for python3
# pyc/pyo files)

# These two macros are defined in the `macros.python3` file, part of python-devel.
# We define them here as well so they are available when building Python
# itself, as Python does not have a BuildRequires on the `python-devel` package
# and thus it's not part of its buildroot.
# Adding a build-time dependency on `python-devel` was contemplated but decided
# against because it could create hard-to-debug issues: python-devel installs
# header files into the buildroot which could be then mistakenly used during
# the building of a newer Python version if there is a bug in the build
# scripts.
# Note that the macros point to a file in the buildroot which will already be
# copied there by the time this macros are invoked in %%__os_install_post.
%{?scl:%global python36_python_provides %{buildroot}%{_root_prefix}/lib/rpm/pythondeps-scl-36.sh --provides %{scl}-}
%{?scl:%global python36_python_requires %{buildroot}%{_root_prefix}/lib/rpm/pythondeps-scl-36.sh --requires %{scl}-}


# ==================
# Top-level metadata
# ==================
Summary: Version 3 of the Python programming language aka Python 3000
Name: %{?scl_prefix}python
Version: %{pybasever}.3
Release: 0.3%{?dist}
License: Python
Group: Development/Languages


# =======================
# Build-time requirements
# =======================

# (keep this list alphabetized)

%{?scl:BuildRequires: %{scl}-runtime}
BuildRequires: autoconf
BuildRequires: bluez-libs-devel
BuildRequires: bzip2
BuildRequires: bzip2-devel
BuildRequires: libdb-devel

# expat 2.1.0 added the symbol XML_SetHashSalt without bumping SONAME.  We use
# it (in pyexpat) in order to enable the fix in Python-3.2.3 for CVE-2012-0876:
BuildRequires: expat-devel

BuildRequires: findutils
BuildRequires: gcc-c++
%if %{with_gdbm}
BuildRequires: gdbm-devel
%endif
BuildRequires: glibc-devel
BuildRequires: gmp-devel
BuildRequires: libffi-devel
BuildRequires: libGL-devel
BuildRequires: libX11-devel
BuildRequires: ncurses-devel
# workaround http://bugs.python.org/issue19804 (test_uuid requires ifconfig)
BuildRequires: net-tools
BuildRequires: openssl-devel
BuildRequires: pkgconfig
BuildRequires: readline-devel
BuildRequires: sqlite-devel

BuildRequires: systemtap-sdt-devel
BuildRequires: systemtap-devel
# (this introduces a dependency on "python", in that systemtap-sdt-devel's
# /usr/bin/dtrace is a python 2 script)
%global tapsetdir      %{_datadir}/systemtap/tapset

BuildRequires: tar
BuildRequires: tcl-devel
BuildRequires: tix-devel
BuildRequires: tk-devel

%if 0%{?with_valgrind}
BuildRequires: valgrind-devel
%endif

BuildRequires: xz-devel
BuildRequires: zlib-devel

%if 0%{?with_rewheel}
BuildRequires: %{?scl_prefix}python-setuptools
BuildRequires: %{?scl_prefix}python-pip
%endif


# =======================
# Source code and patches
# =======================

Source: https://www.python.org/ftp/python/%{version}/Python-%{version}.tar.xz

# Avoid having various bogus auto-generated Provides lines for the various
# python c modules' SONAMEs:

# Supply various useful macros for building python 3 modules:
#  __python3, python3_sitelib, python3_sitearch
Source2: macros.python3

# Supply an RPM macro "py_byte_compile" for the python3-devel subpackage
# to enable specfiles to selectively byte-compile individual files and paths
# with different Python runtimes as necessary:
Source3: macros.pybytecompile

# Systemtap tapset to make it easier to use the systemtap static probes
# (actually a template; LIBRARY_PATH will get fixed up during install)
# Written by dmalcolm; not yet sent upstream
Source5: libpython.stp

# Example systemtap script using the tapset
# Written by wcohen, mjw, dmalcolm; not yet sent upstream
Source6: systemtap-example.stp

# Another example systemtap script that uses the tapset
# Written by dmalcolm; not yet sent upstream
Source7: pyfuntop.stp

# SCL-custom version of pythondeps.sh
# Append 36 to not collide with python27 SCL
Source8: pythondeps-scl-36.sh

# Append 36 for the same reason here
Source9: brp-python-bytecompile-with-scl-python-36

# A simple script to check timestamps of bytecode files
# Run in check section with Python that is currently being built
# Written by bkabrda
Source10:  check-pyc-and-pyo-timestamps.py

# Fixup distutils/unixccompiler.py to remove standard library path from rpath:
# Was Patch0 in ivazquez' python3000 specfile:
Patch1:         Python-3.1.1-rpath.patch

# 00055 #
# Systemtap support: add statically-defined probe points
# Patch sent upstream as http://bugs.python.org/issue14776
# with some subsequent reworking to cope with LANG=C in an rpmbuild
# (where sys.getfilesystemencoding() == 'ascii')
Patch55: 00055-systemtap.patch

Patch102: 00102-lib64.patch

# 00104 #
# Only used when "%%{_lib}" == "lib64"
# Another lib64 fix, for distutils/tests/test_install.py; not upstream:
Patch104: 00104-lib64-fix-for-test_install.patch

# 00111 #
# Patch the Makefile.pre.in so that the generated Makefile doesn't try to build
# a libpythonMAJOR.MINOR.a (bug 550692):
# Downstream only: not appropriate for upstream
Patch111: 00111-no-static-lib.patch

# 00132 #
# Add non-standard hooks to unittest for use in the "check" phase below, when
# running selftests within the build:
#   @unittest._skipInRpmBuild(reason)
# for tests that hang or fail intermittently within the build environment, and:
#   @unittest._expectedFailureInRpmBuild
# for tests that always fail within the build environment
#
# The hooks only take effect if WITHIN_PYTHON_RPM_BUILD is set in the
# environment, which we set manually in the appropriate portion of the "check"
# phase below (and which potentially other python-* rpms could set, to reuse
# these unittest hooks in their own "check" phases)
Patch132: 00132-add-rpmbuild-hooks-to-unittest.patch

# 00137 #
# Some tests within distutils fail when run in an rpmbuild:
Patch137: 00137-skip-distutils-tests-that-fail-in-rpmbuild.patch

# 00146 #
# Support OpenSSL FIPS mode (e.g. when OPENSSL_FORCE_FIPS_MODE=1 is set)
# - handle failures from OpenSSL (e.g. on attempts to use MD5 in a
#   FIPS-enforcing environment)
# - add a new "usedforsecurity" keyword argument to the various digest
#   algorithms in hashlib so that you can whitelist a callsite with
#   "usedforsecurity=False"
# (sent upstream for python 3 as http://bugs.python.org/issue9216 ; see RHEL6
# python patch 119)
# - enforce usage of the _hashlib implementation: don't fall back to the _md5
#   and _sha* modules (leading to clearer error messages if fips selftests
#   fail)
# - don't build the _md5 and _sha* modules; rely on the _hashlib implementation
#   of hashlib
# (rhbz#563986)
# Note: Up to Python 3.4.0.b1, upstream had their own implementation of what
# they assumed would become sha3. This patch was adapted to give it the
# usedforsecurity argument, even though it did nothing (OpenSSL didn't have
# sha3 implementation at that time).In 3.4.0.b2, sha3 implementation was reverted
# (see http://bugs.python.org/issue16113), but the alterations were left in the
# patch, since they may be useful again if upstream decides to rerevert sha3
# implementation and OpenSSL still doesn't support it. For now, they're harmless.

# Patch is updated to be compatible with blake2 and shake algorithms

# As of python 3.6.3, upstream raises a ValueError when a hash function
# fails to be initialized (e.g. in fips mode).
# https://github.com/python/cpython/commit/31b8efeaa893e95358b71eb2b8365552d3966b4a
# Since we carry downstream our own implementation of hashlib for fips mode
# we remove the implementation that was introduced with python 3.6.3 for now.
Patch146: 00146-hashlib-fips.patch

# 00155 #
# Avoid allocating thunks in ctypes unless absolutely necessary, to avoid
# generating SELinux denials on "import ctypes" and "import uuid" when
# embedding Python within httpd (rhbz#814391)
Patch155: 00155-avoid-ctypes-thunks.patch

# 00157 #
# Update uid/gid handling throughout the standard library: uid_t and gid_t are
# unsigned 32-bit values, but existing code often passed them through C long
# values, which are signed 32-bit values on 32-bit architectures, leading to
# negative int objects for uid/gid values >= 2^31 on 32-bit architectures.
#
# Introduce _PyObject_FromUid/Gid to convert uid_t/gid_t values to python
# objects, using int objects where the value will fit (long objects otherwise),
# and _PyArg_ParseUid/Gid to convert int/long to uid_t/gid_t, with -1 allowed
# as a special case (since this is given special meaning by the chown syscall)
#
# Update standard library to use this throughout for uid/gid values, so that
# very large uid/gid values are round-trippable, and -1 remains usable.
# (rhbz#697470)
Patch157: 00157-uid-gid-overflows.patch

# 00160 #
# Python 3.3 added os.SEEK_DATA and os.SEEK_HOLE, which may be present in the
# header files in the build chroot, but may not be supported in the running
# kernel, hence we disable this test in an rpm build.
# Adding these was upstream issue http://bugs.python.org/issue10142
# Not yet sent upstream
Patch160: 00160-disable-test_fs_holes-in-rpm-build.patch

# 00163 #
# Some tests within test_socket fail intermittently when run inside Koji;
# disable them using unittest._skipInRpmBuild
# Not yet sent upstream
Patch163: 00163-disable-parts-of-test_socket-in-rpm-build.patch

# 00170 #
# In debug builds, try to print repr() when a C-level assert fails in the
# garbage collector (typically indicating a reference-counting error
# somewhere else e.g in an extension module)
# Backported to 2.7 from a patch I sent upstream for py3k
#   http://bugs.python.org/issue9263  (rhbz#614680)
# hiding the proposed new macros/functions within gcmodule.c to avoid exposing
# them within the extension API.
# (rhbz#850013
Patch170: 00170-gc-assertions.patch

# 00178 #
# Don't duplicate various FLAGS in sysconfig values
# http://bugs.python.org/issue17679
# Does not affect python2 AFAICS (different sysconfig values initialization)
Patch178: 00178-dont-duplicate-flags-in-sysconfig.patch

# 00180 #
# Enable building on ppc64p7
# Not appropriate for upstream, Fedora-specific naming
Patch180: 00180-python-add-support-for-ppc64p7.patch

# 00186 #
# Fix for https://bugzilla.redhat.com/show_bug.cgi?id=1023607
# Previously, this fixed a problem where some *.py files were not being
# bytecompiled properly during build. This was result of py_compile.compile
# raising exception when trying to convert test file with bad encoding, and
# thus not continuing bytecompilation for other files.
# This was fixed upstream, but the test hasn't been merged yet, so we keep it
Patch186: 00186-dont-raise-from-py_compile.patch

# 00188 #
# Downstream only patch that should be removed when we compile all guaranteed
# hashlib algorithms properly. The problem is this:
# - during tests, test_hashlib is imported and executed before test_lib2to3
# - if at least one hash function has failed, trying to import it triggers an
#   exception that is being caught and exception is logged:
#   http://hg.python.org/cpython/file/2de806c8b070/Lib/hashlib.py#l217
# - logging the exception makes logging module run basicConfig
# - when lib2to3 tests are run again, lib2to3 runs basicConfig again, which
#   doesn't do anything, because it was run previously
#   (logging.root.handlers != []), which means that the default setup
#   (most importantly logging level) is not overriden. That means that a test
#   relying on this will fail (test_filename_changing_on_output_single_dir)
Patch188: 00188-fix-lib2to3-tests-when-hashlib-doesnt-compile-properly.patch

# 00189 #
# Add the rewheel module, allowing to recreate wheels from already installed
# ones
# https://github.com/bkabrda/rewheel
Patch189: 00189-add-rewheel-module.patch

# 00205 #
# LIBPL variable in makefile takes LIBPL from configure.ac
# but the LIBPL variable defined there doesn't respect libdir macro
Patch205: 00205-make-libpl-respect-lib64.patch

# 00206 #
# Remove hf flag from arm triplet which is used
# by debian but fedora infra uses only eabi without hf
Patch206: 00206-remove-hf-from-arm-triplet.patch

# 00231 #
# Add choices for sort option of cProfile for better output message
# http://bugs.python.org/issue23420
# Resolves: rhbz#1326287
Patch231: 00231-cprofile-sort-option.patch

# 00243 #
# Fix the triplet used on 64-bit MIPS
# rhbz#1322526: https://bugzilla.redhat.com/show_bug.cgi?id=1322526
# Upstream uses Debian-like style mips64-linux-gnuabi64
# Fedora needs the default mips64-linux-gnu
Patch243: 00243-fix-mips64-triplet.patch

# 00264 #
# Fix pass by value for structs on 64-bit Cygwin/MinGW/aarch64
# Fixed upstream: http://bugs.python.org/issue29804
Patch264: 00264-fix-pass-by-value-for-structs-on-aarch64.patch

# 00277 #
# Fix test_exception_errpipe_bad_data() and
# test_exception_errpipe_normal() of test_subprocess: mock os.waitpid()
# to avoid calling the real os.waitpid(0, 0) which is an unexpected
# side effect of the test, which makes the brew builds hang.
Patch277: 00277-fix-test-subprocess-hanging-tests.patch

# 00278 #
# skip test_sha256 from test_socket, as it relies on the implementation
# of kernel's crypto API  and the behaviour is not consistent for powerpc
# architectures, making the test fail.
# Reported upstream: https://bugs.python.org/issue31705
#
# Issue manifests on any architecture on kernel < 4.5.
# Original patch replaced with upstream-accepted one.
Patch278: 00278-skip-test-sha256.patch

Patch300: 00300-change-so-version-scl.patch

# (New patches go here ^^^)
#
# When adding new patches to "python" and "python3" in Fedora, EL, etc.,
# please try to keep the patch numbers in-sync between all specfiles.
#
# More information, and a patch number catalog, is at:
#
#     https://fedoraproject.org/wiki/SIGs/Python/PythonPatches


# add correct arch for ppc64/ppc64le
# it should be ppc64le-linux-gnu/ppc64-linux-gnu instead powerpc64le-linux-gnu/powerpc64-linux-gnu
Patch5001: python3-powerppc-arch.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-root

# ======================================================
# Additional metadata, and subpackages
# ======================================================

URL: https://www.python.org/

Provides: %{?scl_prefix}python(abi) = %{pybasever}

Requires: %{?scl_prefix}%{pkg_name}-libs%{?_isa} = %{version}-%{release}
%{?scl:Requires: %{scl}-runtime}
%if 0%{with_rewheel}
Requires: %{?scl_prefix}python-setuptools
Requires: %{?scl_prefix}python-pip
%endif

%description
Python 3 is a new version of the language that is incompatible with the 2.x
line of releases. The language is mostly the same, but many details, especially
how built-in objects like dictionaries and strings work, have changed
considerably, and a lot of deprecated features have finally been removed.

%package libs
Summary:        Python 3 runtime libraries
Group:          Development/Libraries
%{?scl:Requires:       %{scl}-runtime}
#Requires:       %%{name} = %%{version}-%%{release}

# expat 2.1.0 added the symbol XML_SetHashSalt without bumping SONAME.  We use
# this symbol (in pyexpat), so we must explicitly state this dependency to
# prevent "import pyexpat" from failing with a linker error if someone hasn't
# yet upgraded expat:
Requires: expat >= 2.1.0

%description libs
This package contains files used to embed Python 3 into applications.

%package devel
Summary: Libraries and header files needed for Python 3 development
Group: Development/Libraries
Requires: %{?scl_prefix}%{pkg_name}%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}%{pkg_name}-libs%{?_isa} = %{version}-%{release}
# we filtered provides of pkgconfig on rhel7 so we need to manully re add them
Provides: %{?scl_prefix}pkgconfig(python) = %{version}-%{release}
Provides: %{?scl_prefix}pkgconfig(python-3.6m) = %{version}-%{release}
Provides: %{?scl_prefix}pkgconfig(python-3.6) = %{version}-%{release}
Provides: %{?scl_prefix}pkgconfig(python3) = %{version}-%{release}
Conflicts: %{?scl_prefix}%{pkg_name} < %{version}-%{release}

# Fix for rhbz#1144601
Requires:       scl-utils-build

%description devel
This package contains libraries and header files used to build applications
with and native libraries for Python 3

%package tools
Summary: A collection of tools included with Python 3
Group: Development/Tools
Requires: %{?scl_prefix}%{pkg_name} = %{version}-%{release}
Requires: %{?scl_prefix}%{pkg_name}-tkinter = %{version}-%{release}

%description tools
This package contains several tools included with Python 3

%package tkinter
Summary: A GUI toolkit for Python 3
Group: Development/Languages
Requires: %{?scl_prefix}%{pkg_name} = %{version}-%{release}

%description tkinter
The Tkinter (Tk interface) program is an graphical user interface for
the Python scripting language.

%package test
Summary: The test modules from the main python 3 package
Group: Development/Languages
Requires: %{?scl_prefix}%{pkg_name} = %{version}-%{release}
Requires: %{?scl_prefix}%{pkg_name}-tools = %{version}-%{release}

%description test
The test modules from the main %{name} package.
These are in a separate package to save space, as they are almost never used
in production.

You might want to install the python3-test package if you're developing
python 3 code that uses more than just unittest and/or test_support.py.

%if 0%{?with_debug_build}
%package debug
Summary: Debug version of the Python 3 runtime
Group: Applications/System

# The debug build is an all-in-one package version of the regular build, and
# shares the same .py/.pyc files and directories as the regular build.  Hence
# we depend on all of the subpackages of the regular build:
Requires: %{?scl_prefix}%{pkg_name}%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}%{pkg_name}-libs%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}%{pkg_name}-devel%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}%{pkg_name}-test%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}%{pkg_name}-tkinter%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}%{pkg_name}-tools%{?_isa} = %{version}-%{release}
# we filtered provides of pkgconfig on rhel7 so we need to manully re add them
Provides: %{?scl_prefix}pkgconfig(python-3.6dm) = %{version}-%{release}

%description debug
python3-debug provides a version of the Python 3 runtime with numerous debugging
features enabled, aimed at advanced Python users, such as developers of Python
extension modules.

This version uses more memory and will be slower than the regular Python 3 build,
but is useful for tracking down reference-counting issues, and other bugs.

The bytecodes are unchanged, so that .pyc files are compatible between the two
versions of Python 3, but the debugging features mean that C/C++ extension
modules are ABI-incompatible with those built for the standard runtime.

It shares installation directories with the standard Python 3 runtime, so that
.py and .pyc files can be shared.  All compiled extension modules gain a "_d"
suffix ("foo_d.so" rather than "foo.so") so that each Python 3 implementation
can load its own extensions.
%endif # with_debug_build

# ======================================================
# The prep phase of the build:
# ======================================================

%prep
%setup -q -n Python-%{version}

%if 0%{?with_systemtap}
# Provide an example of usage of the tapset:
cp -a %{SOURCE6} .
cp -a %{SOURCE7} .
%endif # with_systemtap

# Ensure that we're using the system copy of various libraries, rather than
# copies shipped by upstream in the tarball:
#   Remove embedded copy of expat:
rm -r Modules/expat || exit 1

#   Remove embedded copy of zlib:
rm -r Modules/zlib || exit 1

# Don't build upstream Python's implementation of these crypto algorithms;
# instead rely on _hashlib and OpenSSL.
#
# For example, in our builds hashlib.md5 is implemented within _hashlib via
# OpenSSL (and thus respects FIPS mode), and does not fall back to _md5
# TODO: there seems to be no OpenSSL support in Python for sha3 so far
# when it is there, also remove _sha3/ dir
for f in md5module.c sha1module.c sha256module.c sha512module.c; do
    rm Modules/$f
done

%if 0%{with_rewheel}
%global pip_version 9.0.1
sed -r -i s/'_PIP_VERSION = "[0-9.]+"'/'_PIP_VERSION = "%{pip_version}"'/ Lib/ensurepip/__init__.py
%endif

#
# Apply patches:
#
%patch1 -p1

%if 0%{?with_systemtap}
%patch55 -p1 -b .systemtap
%endif

%if "%{_lib}" == "lib64"
%patch102 -p1
%patch104 -p1
%endif
%patch111 -p1

%patch132 -p1
%patch137 -p1
%patch146 -p1
%patch155 -p1
%patch157 -p1
%patch160 -p1
%patch163 -p1
%patch170 -p1
%patch178 -p1
%patch180 -p1
%patch186 -p1
%patch188 -p1

%if 0%{with_rewheel}
%patch189 -p1
%endif

%patch205 -p1
%patch206 -p1
%patch231 -p1
%patch243 -p1
%patch264 -p1
%patch277 -p1
%patch278 -p1

cat %{PATCH300} | sed -e "s/__SCL_NAME__/%{?scl}/" \
                | patch -p1

# Currently (2010-01-15), http://docs.python.org/library is for 2.6, and there
# are many differences between 2.6 and the Python 3 library.
#
# Fix up the URLs within pydoc to point at the documentation for this
# MAJOR.MINOR version:
#
sed --in-place \
    --expression="s|http://docs.python.org/library|http://docs.python.org/%{pybasever}/library|g" \
    Lib/pydoc.py || exit 1

%patch5001 -p1

# ======================================================
# Configuring and building the code:
# ======================================================


# filter pkgconfig Requires/Provides on rhel7 as filter_from doesnt work there
%global __provides_exclude ^pkgconfig\\(.*$

%build
export topdir=$(pwd)
export CFLAGS="-I%{_includedir} $RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export CXXFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export CPPFLAGS="-I%{_includedir}`pkg-config --cflags-only-I libffi`"
export OPT="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export LINKCC="gcc"
export CFLAGS="$CFLAGS `pkg-config --cflags openssl`"
# Passing to the dynamic linker parameters -rpath and --enable-new-dtags causes
# ld to set RUNPATH instead of RPATH in the executables and libraries
# Setting RUNPATH resolves rhbz#1479406
export LDFLAGS="-L%{_libdir}$RPM_LD_FLAGS `pkg-config --libs-only-L openssl` \
                -Wl,-rpath,%{_libdir} -Wl,--enable-new-dtags"

# Define a function, for how to perform a "build" of python for a given
# configuration:
BuildPython() {
  ConfName=$1
  BinaryName=$2
  SymlinkName=$3
  ExtraConfigArgs=$4
  PathFixWithThisBinary=$5
  MoreCFlags=$6

  ConfDir=build/$ConfName

  echo STARTING: BUILD OF PYTHON FOR CONFIGURATION: $ConfName - %{_bindir}/$BinaryName
  mkdir -p $ConfDir

  pushd $ConfDir

  # Use the freshly created "configure" script, but in the directory two above:
  %global _configure $topdir/configure

%configure \
  --enable-ipv6 \
  --enable-shared \
  --with-computed-gotos=%{with_computed_gotos} \
  --with-dbmliborder=gdbm:ndbm:bdb \
  --with-system-expat \
  --with-system-ffi \
  --enable-loadable-sqlite-extensions \
  --with-dtrace \
%if 0%{?with_valgrind}
  --with-valgrind \
%endif
  $ExtraConfigArgs \
  %{nil}

  # Set EXTRA_CFLAGS to our CFLAGS (rather than overriding OPT, as we've done
  # in the past).
  # This should fix a problem with --with-valgrind where it adds
  #   -DDYNAMIC_ANNOTATIONS_ENABLED=1
  # to OPT which must be passed to all compilation units in the build,
  # otherwise leading to linker errors, e.g.
  #    missing symbol AnnotateRWLockDestroy
  #
  # Invoke the build:
  make EXTRA_CFLAGS="$CFLAGS $MoreCFlags" %{?_smp_mflags}

  popd
  echo FINISHED: BUILD OF PYTHON FOR CONFIGURATION: $ConfDir
}

export -f BuildPython
# Use "BuildPython" to support building with different configurations:

%{?scl:scl enable %scl - << \EOF}
%if 0%{?with_debug_build}
BuildPython debug \
  python-debug \
  python%{pybasever}-debug \
%ifarch %{ix86} x86_64 ppc %{power64}
  "--with-pydebug --without-ensurepip" \
%else
  "--with-pydebug --without-ensurepip" \
%endif
  false \
  -O0
%endif # with_debug_build

BuildPython optimized \
  python \
  python%{pybasever} \
%ifarch %{ix86} x86_64
  "--without-ensurepip --enable-optimizations" \
%else
  "--without-ensurepip" \
%endif
  true
%{?scl:EOF}

# ======================================================
# Installing the built code:
# ======================================================

%install
topdir=$(pwd)
rm -fr %{buildroot}
mkdir -p %{buildroot}%{_prefix} %{buildroot}%{_mandir}

# install SCL custom RPM scripts
%{?scl:mkdir -p %{buildroot}%{_root_prefix}/lib/rpm/redhat}
%{?scl:cp -a %{SOURCE8} %{buildroot}%{_root_prefix}/lib/rpm}
%{?scl:cp -a %{SOURCE9} %{buildroot}%{_root_prefix}/lib/rpm/redhat}

InstallPython() {

  ConfName=$1
  PyInstSoName=$2
  MoreCFlags=$3

  ConfDir=build/$ConfName

  echo STARTING: INSTALL OF PYTHON FOR CONFIGURATION: $ConfName
  mkdir -p $ConfDir

  pushd $ConfDir

make install DESTDIR=%{buildroot} INSTALL="install -p" EXTRA_CFLAGS="$MoreCFlags"

  popd

  # We install a collection of hooks for gdb that make it easier to debug
  # executables linked against libpython3* (such as /usr/bin/python3 itself)
  #
  # These hooks are implemented in Python itself (though they are for the version
  # of python that gdb is linked with, in this case Python 2.7)
  #
  # gdb-archer looks for them in the same path as the ELF file, with a -gdb.py suffix.
  # We put them in the debuginfo package by installing them to e.g.:
  #  /usr/lib/debug/usr/lib/libpython3.2.so.1.0.debug-gdb.py
  #
  # See https://fedoraproject.org/wiki/Features/EasierPythonDebugging for more
  # information
  #
  # Copy up the gdb hooks into place; the python file will be autoloaded by gdb
  # when visiting libpython.so, provided that the python file is installed to the
  # same path as the library (or its .debug file) plus a "-gdb.py" suffix, e.g:
  #  /usr/lib/debug/usr/lib64/libpython3.2.so.1.0.debug-gdb.py
  # (note that the debug path is /usr/lib/debug for both 32/64 bit)
  #
  # Initially I tried:
  #  /usr/lib/libpython3.1.so.1.0-gdb.py
  # but doing so generated noise when ldconfig was rerun (rhbz:562980)
  #
%if 0%{?with_gdb_hooks}
  DirHoldingGdbPy=%{?scl:%_root_prefix}%{!?scl:%_prefix}/lib/debug/%{_libdir}
  PathOfGdbPy=$DirHoldingGdbPy/$PyInstSoName.debug-gdb.py

  mkdir -p %{buildroot}$DirHoldingGdbPy
  cp Tools/gdb/libpython.py %{buildroot}$PathOfGdbPy
%endif # with_gdb_hooks

  echo FINISHED: INSTALL OF PYTHON FOR CONFIGURATION: $ConfName
}

# Use "InstallPython" to support building with different configurations:

# Install the "debug" build first, so that we can move some files aside
%if 0%{?with_debug_build}
InstallPython debug \
  %{py_INSTSONAME_debug} \
  -O0
%endif # with_debug_build

# Now the optimized build:
InstallPython optimized \
  %{py_INSTSONAME_optimized}

install -d -m 0755 ${RPM_BUILD_ROOT}%{pylibdir}/site-packages/__pycache__

ln -s %{_bindir}/2to3 ${RPM_BUILD_ROOT}%{_bindir}/python3-2to3

# Development tools
install -m755 -d ${RPM_BUILD_ROOT}%{pylibdir}/Tools
install Tools/README ${RPM_BUILD_ROOT}%{pylibdir}/Tools/
cp -ar Tools/freeze ${RPM_BUILD_ROOT}%{pylibdir}/Tools/
cp -ar Tools/i18n ${RPM_BUILD_ROOT}%{pylibdir}/Tools/
cp -ar Tools/pynche ${RPM_BUILD_ROOT}%{pylibdir}/Tools/
cp -ar Tools/scripts ${RPM_BUILD_ROOT}%{pylibdir}/Tools/

# pynche
cat > ${RPM_BUILD_ROOT}%{_bindir}/pynche << EOF
#!/bin/bash
exec %{pylibdir}/Tools/pynche/pynche
EOF
chmod 755 ${RPM_BUILD_ROOT}%{_bindir}/pynche

# Documentation tools
install -m755 -d %{buildroot}%{pylibdir}/Doc
cp -ar Doc/tools %{buildroot}%{pylibdir}/Doc/

# Demo scripts
cp -ar Tools/demo %{buildroot}%{pylibdir}/Tools/

# Fix for bug #136654
rm -f %{buildroot}%{pylibdir}/email/test/data/audiotest.au %{buildroot}%{pylibdir}/test/audiotest.au

%if "%{_lib}" == "lib64"
install -d -m 0755 %{buildroot}/%{_prefix}/lib/python%{pybasever}/site-packages/__pycache__
%endif

# Make python3-devel multilib-ready (bug #192747, #139911)
%global _pyconfig32_h pyconfig-32.h
%global _pyconfig64_h pyconfig-64.h

%ifarch %{power64} s390x x86_64 ia64 alpha sparc64 aarch64 %{mips64} riscv64
%global _pyconfig_h %{_pyconfig64_h}
%else
%global _pyconfig_h %{_pyconfig32_h}
%endif

# ABIFLAGS, LDVERSION and SOABI are in the upstream Makefile
%global ABIFLAGS_optimized m
%global ABIFLAGS_debug     dm

%global LDVERSION_optimized %{pybasever}%{ABIFLAGS_optimized}
%global LDVERSION_debug     %{pybasever}%{ABIFLAGS_debug}

%global SOABI_optimized cpython-%{pyshortver}%{ABIFLAGS_optimized}-%{_arch}-linux%{_gnu}
%global SOABI_debug     cpython-%{pyshortver}%{ABIFLAGS_debug}-%{_arch}-linux%{_gnu}

%if 0%{?with_debug_build}
%global PyIncludeDirs python%{LDVERSION_optimized} python%{LDVERSION_debug}

%else
%global PyIncludeDirs python%{LDVERSION_optimized}
%endif

for PyIncludeDir in %{PyIncludeDirs} ; do
  mv %{buildroot}%{_includedir}/$PyIncludeDir/pyconfig.h \
     %{buildroot}%{_includedir}/$PyIncludeDir/%{_pyconfig_h}
  cat > %{buildroot}%{_includedir}/$PyIncludeDir/pyconfig.h << EOF
#include <bits/wordsize.h>

#if __WORDSIZE == 32
#include "%{_pyconfig32_h}"
#elif __WORDSIZE == 64
#include "%{_pyconfig64_h}"
#else
#error "Unknown word size"
#endif
EOF
done

# Fix for bug 201434: make sure distutils looks at the right pyconfig.h file
# Similar for sysconfig: sysconfig.get_config_h_filename tries to locate
# pyconfig.h so it can be parsed, and needs to do this at runtime in site.py
# when python starts up (bug 653058)
#
# Split this out so it goes directly to the pyconfig-32.h/pyconfig-64.h
# variants:
sed -i -e "s/'pyconfig.h'/'%{_pyconfig_h}'/" \
  %{buildroot}%{pylibdir}/distutils/sysconfig.py \
  %{buildroot}%{pylibdir}/sysconfig.py

# Switch all shebangs to refer to the specific Python version.
LD_LIBRARY_PATH=./build/optimized ./build/optimized/python \
  Tools/scripts/pathfix.py \
  -i "%{_bindir}/python%{pybasever}" \
  %{buildroot}

# Remove shebang lines from .py files that aren't executable, and
# remove executability from .py files that don't have a shebang line:
find %{buildroot} -name \*.py \
  \( \( \! -perm /u+x,g+x,o+x -exec sed -e '/^#!/Q 0' -e 'Q 1' {} \; \
  -print -exec sed -i '1d' {} \; \) -o \( \
  -perm /u+x,g+x,o+x ! -exec grep -m 1 -q '^#!' {} \; \
  -exec chmod a-x {} \; \) \)

# .xpm and .xbm files should not be executable:
find %{buildroot} \
  \( -name \*.xbm -o -name \*.xpm -o -name \*.xpm.1 \) \
  -exec chmod a-x {} \;

# Remove executable flag from files that shouldn't have it:
chmod a-x \
  %{buildroot}%{pylibdir}/distutils/tests/Setup.sample \
  %{buildroot}%{pylibdir}/Tools/README

# Get rid of DOS batch files:
find %{buildroot} -name \*.bat -exec rm {} \;

# Get rid of backup files:
find %{buildroot}/ -name "*~" -exec rm -f {} \;
find . -name "*~" -exec rm -f {} \;
rm -f %{buildroot}%{pylibdir}/LICENSE.txt
# Junk, no point in putting in -test sub-pkg
rm -f ${RPM_BUILD_ROOT}/%{pylibdir}/idlelib/testcode.py*

# Get rid of stray patch file from buildroot:
rm -f %{buildroot}%{pylibdir}/test/test_imp.py.apply-our-changes-to-expected-shebang # from patch 4

# Fix end-of-line encodings:
find %{buildroot}/ -name \*.py -exec sed -i 's/\r//' {} \;

# Fix an encoding:
iconv -f iso8859-1 -t utf-8 %{buildroot}/%{pylibdir}/Demo/rpc/README > README.conv && mv -f README.conv %{buildroot}/%{pylibdir}/Demo/rpc/README

# Note that
#  %{pylibdir}/Demo/distutils/test2to3/setup.py
# is in iso-8859-1 encoding, and that this is deliberate; this is test data
# for the 2to3 tool, and one of the functions of the 2to3 tool is to fixup
# character encodings within python source code

# Do bytecompilation with the newly installed interpreter.
# This is similar to the script in macros.pybytecompile
# compile *.pyc
find %{buildroot} -type f -a -name "*.py" -print0 | \
    LD_LIBRARY_PATH="%{buildroot}%{dynload_dir}/:%{buildroot}%{_libdir}" \
    PYTHONPATH="%{buildroot}%{_libdir}/python%{pybasever} %{buildroot}%{_libdir}/python%{pybasever}/site-packages" \
    xargs -0 %{buildroot}%{_bindir}/python%{pybasever} -O -c 'import py_compile, sys; [py_compile.compile(f, dfile=f.partition("%{buildroot}")[2], optimize=opt) for opt in range(3) for f in sys.argv[1:]]' || :

# Fixup permissions for shared libraries from non-standard 555 to standard 755:
find %{buildroot} \
    -perm 555 -exec chmod 755 {} \;

# Install macros for rpm:
mkdir -p %{buildroot}/%{?scl:%_root_sysconfdir}%{!?scl:%_sysconfdir}/rpm
install -m 644 %{SOURCE2} %{buildroot}/%{?scl:%_root_sysconfdir}%{!?scl:%_sysconfdir}/rpm
install -m 644 %{SOURCE3} %{buildroot}/%{?scl:%_root_sysconfdir}%{!?scl:%_sysconfdir}/rpm
# Optionally rename macro files by appending scl name
pushd %{buildroot}/%{?scl:%_root_sysconfdir}%{!?scl:%_sysconfdir}
find -type f -name 'macros.py*' -exec mv {} {}%{?scl:.%{scl}} \;
popd

%{?scl:sed -i 's|^\(%@scl@__python3\)|\1 %{_bindir}/python3|' %{buildroot}%{_root_sysconfdir}/rpm/macros.python3.%{scl}}
# We replace @scl@ with scl_no_vendor macro from build meta subpackage because macros names cant contain
# dash, scl_no_vendor is scl macro without vendor prefix
%{?scl:sed -i 's|@scl@|%{scl_no_vendor}|g' %{buildroot}%{_root_sysconfdir}/rpm/macros.python3.%{scl}}
# when using scl enable we have to pass original scl macro with vendor prefix
%{?scl:sed -i 's|@vendorscl@|%{scl}|g' %{buildroot}%{_root_sysconfdir}/rpm/macros.python3.%{scl}}

# Ensure that the curses module was linked against libncursesw.so, rather than
# libncurses.so (bug 539917)
ldd %{buildroot}/%{dynload_dir}/_curses*.so \
    | grep curses \
    | grep libncurses.so && (echo "_curses.so linked against libncurses.so" ; exit 1)

# Ensure that the debug modules are linked against the debug libpython, and
# likewise for the optimized modules and libpython:
for Module in %{buildroot}/%{dynload_dir}/*.so ; do
    case $Module in
    *.%{SOABI_debug})
        ldd $Module | grep %{py_INSTSONAME_optimized} &&
            (echo Debug module $Module linked against optimized %{py_INSTSONAME_optimized} ; exit 1)

        ;;
    *.%{SOABI_optimized})
        ldd $Module | grep %{py_INSTSONAME_debug} &&
            (echo Optimized module $Module linked against debug %{py_INSTSONAME_debug} ; exit 1)
        ;;
    esac
done

# Create "/usr/bin/python3-debug", a symlink to the python3 debug binary, to
# avoid the user having to know the precise version and ABI flags.  (see
# e.g. rhbz#676748):
%if 0%{?with_debug_build}
ln -s \
  %{_bindir}/python%{LDVERSION_debug} \
  %{buildroot}%{_bindir}/python3-debug
%endif

#
# Systemtap hooks:
#
%if 0%{?with_systemtap}
# Install a tapset for this libpython into tapsetdir, fixing up the path to the
# library:
mkdir -p %{buildroot}%{tapsetdir}
%ifarch %{power64} s390x x86_64 ia64 alpha sparc64 aarch64 %{mips64}
%global libpython_stp_optimized libpython%{pybasever}-64.stp
%global libpython_stp_debug     libpython%{pybasever}-debug-64.stp
%else
%global libpython_stp_optimized libpython%{pybasever}-32.stp
%global libpython_stp_debug     libpython%{pybasever}-debug-32.stp
%endif

sed \
   -e "s|LIBRARY_PATH|%{_libdir}/%{py_INSTSONAME_optimized}|" \
   %{_sourcedir}/libpython.stp \
   > %{buildroot}%{tapsetdir}/%{libpython_stp_optimized}

%if 0%{?with_debug_build}
# In Python 3, python3 and python3-debug don't point to the same binary,
# so we have to replace "python3" with "python3-debug" to get systemtap
# working with debug build
sed \
   -e "s|LIBRARY_PATH|%{_libdir}/%{py_INSTSONAME_debug}|" \
   -e 's|"python3"|"python3-debug"|' \
   %{_sourcedir}/libpython.stp \
   > %{buildroot}%{tapsetdir}/%{libpython_stp_debug}
%endif # with_debug_build

%endif # with_systemtap

# Create symlinks python* for python3* binaries (and similar)
pushd %{buildroot}%{_bindir}
for versioned_binary in idle3 pydoc3 python3-2to3 python3 python3-config; do
  non_versioned_binary=$(echo $versioned_binary | sed -e 's/python3/python/' -e 's/idle3/idle/' -e 's/pydoc3/pydoc/')
  ln -s $versioned_binary $non_versioned_binary
done
%if 0%{?with_debug_build}
  ln -s python3-debug python-debug
%endif
popd

# Create symlink python.pc for python3.pc
pushd %{buildroot}%{_libdir}/pkgconfig
ln -s python3.pc python.pc
popd

# Create a python manpage (rhbz#1072522)
cp %{buildroot}%{_mandir}/man1/python%{pybasever}.1 %{buildroot}%{_mandir}/man1/python.1

# Rename the -devel script that differs on different arches to arch specific name
mv %{buildroot}%{_bindir}/python%{LDVERSION_optimized}-{,`uname -m`-}config
echo -e '#!/bin/sh\nexec `dirname $0`/python%{LDVERSION_optimized}-`uname -m`-config "$@"' > \
  %{buildroot}%{_bindir}/python%{LDVERSION_optimized}-config
echo '[ $? -eq 127 ] && echo "Could not find python%{LDVERSION_optimized}-`uname -m`-config. Look around to see available arches." >&2' >> \
  %{buildroot}%{_bindir}/python%{LDVERSION_optimized}-config
  chmod +x %{buildroot}%{_bindir}/python%{LDVERSION_optimized}-config

%if 0%{?with_debug_build}
# Rename the -debug script that differs on different arches to arch specific name
mv %{buildroot}%{_bindir}/python%{LDVERSION_debug}-{,`uname -m`-}config
echo -e '#!/bin/sh\nexec `dirname $0`/python%{LDVERSION_debug}-`uname -m`-config "$@"' > \
  %{buildroot}%{_bindir}/python%{LDVERSION_debug}-config
echo '[ $? -eq 127 ] && echo "Could not find python%{LDVERSION_debug}-`uname -m`-config. Look around to see available arches." >&2' >> \
  %{buildroot}%{_bindir}/python%{LDVERSION_debug}-config
  chmod +x %{buildroot}%{_bindir}/python%{LDVERSION_debug}-config
%endif # with_debug_build


# ======================================================
# Running the upstream test suite
# ======================================================

%check

# first of all, check timestamps of bytecode files
find %{buildroot} -type f -a -name "*.py" -print0 | \
    LD_LIBRARY_PATH="%{buildroot}%{dynload_dir}/:%{buildroot}%{_libdir}" \
    PYTHONPATH="%{buildroot}%{_libdir}/python%{pybasever} %{buildroot}%{_libdir}/python%{pybasever}/site-packages" \
    xargs -0 %{buildroot}%{_bindir}/python%{pybasever} %{SOURCE10}


topdir=$(pwd)
CheckPython() {
  ConfName=$1
  ConfDir=$(pwd)/build/$ConfName

  echo STARTING: CHECKING OF PYTHON FOR CONFIGURATION: $ConfName

  # Note that we're running the tests using the version of the code in the
  # builddir, not in the buildroot.

  # Run the upstream test suite, setting "WITHIN_PYTHON_RPM_BUILD" so that the
  # our non-standard decorators take effect on the relevant tests:
  #   @unittest._skipInRpmBuild(reason)
  #   @unittest._expectedFailureInRpmBuild
  # test_faulthandler.test_register_chain currently fails on ppc64le and
  #   aarch64, see upstream bug http://bugs.python.org/issue21131
  WITHIN_PYTHON_RPM_BUILD= \
  LD_LIBRARY_PATH=$ConfDir $ConfDir/python -m test.regrtest \
    -wW --slowest --findleaks \
    -x test_distutils \
    -x test_readline \
    %ifarch ppc64le aarch64
    -x test_faulthandler \
    %endif
    %ifarch %{mips64}
    -x test_ctypes \
    %endif
    %ifarch %{power64} s390 s390x armv7hl aarch64 %{mips}
    -x test_gdb
    %endif

  echo FINISHED: CHECKING OF PYTHON FOR CONFIGURATION: $ConfName

}

export -f CheckPython

%if 0%{run_selftest_suite}

%{?scl:scl enable %scl - << \EOF}
set -e
# Check each of the configurations:
%if 0%{?with_debug_build}
CheckPython debug
%endif # with_debug_build
CheckPython optimized
%{?scl:EOF}

%endif # run_selftest_suite


# ======================================================
# Cleaning up
# ======================================================

%clean
rm -fr %{buildroot}


# ======================================================
# Scriptlets
# ======================================================

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig



%files
%defattr(-, root, root)
%doc LICENSE README.rst
%{_bindir}/pydoc*
%{_bindir}/python
%{_bindir}/python3
%{_bindir}/python%{pybasever}
%{_bindir}/python%{pybasever}m
%{_bindir}/pyvenv
%{_bindir}/pyvenv-%{pybasever}
%{_mandir}/*/*

%files libs
%defattr(-,root,root,-)
%doc LICENSE README.rst
%dir %{pylibdir}
%dir %{dynload_dir}

%{pylibdir}/lib2to3
%exclude %{pylibdir}/lib2to3/tests

%dir %{pylibdir}/unittest/
%dir %{pylibdir}/unittest/__pycache__/
%{pylibdir}/unittest/*.py
%{pylibdir}/unittest/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/asyncio/
%dir %{pylibdir}/asyncio/__pycache__/
%{pylibdir}/asyncio/*.py
%{pylibdir}/asyncio/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/venv/
%dir %{pylibdir}/venv/__pycache__/
%{pylibdir}/venv/*.py
%{pylibdir}/venv/__pycache__/*%{bytecode_suffixes}
%{pylibdir}/venv/scripts

%{pylibdir}/wsgiref
%{pylibdir}/xmlrpc

%dir %{pylibdir}/ensurepip/
%dir %{pylibdir}/ensurepip/__pycache__/
%{pylibdir}/ensurepip/*.py
%{pylibdir}/ensurepip/__pycache__/*%{bytecode_suffixes}
%exclude %{pylibdir}/ensurepip/_bundled

%if 0%{?with_rewheel}
%dir %{pylibdir}/ensurepip/rewheel/
%dir %{pylibdir}/ensurepip/rewheel/__pycache__/
%{pylibdir}/ensurepip/rewheel/*.py
%{pylibdir}/ensurepip/rewheel/__pycache__/*%{bytecode_suffixes}
%endif

%{pylibdir}/idlelib

%dir %{pylibdir}/test/
%dir %{pylibdir}/test/__pycache__/
%dir %{pylibdir}/test/support/
%dir %{pylibdir}/test/support/__pycache__/
%{pylibdir}/test/__init__.py
%{pylibdir}/test/__pycache__/__init__%{bytecode_suffixes}
%{pylibdir}/test/support/__init__.py
%{pylibdir}/test/support/__pycache__/__init__%{bytecode_suffixes}

%dir %{pylibdir}/concurrent/
%dir %{pylibdir}/concurrent/__pycache__/
%{pylibdir}/concurrent/*.py
%{pylibdir}/concurrent/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/concurrent/futures/
%dir %{pylibdir}/concurrent/futures/__pycache__/
%{pylibdir}/concurrent/futures/*.py
%{pylibdir}/concurrent/futures/__pycache__/*%{bytecode_suffixes}

%{pylibdir}/pydoc_data

%{dynload_dir}/_blake2.%{SOABI_optimized}.so
%{dynload_dir}/_sha3.%{SOABI_optimized}.so

%{dynload_dir}/_asyncio.%{SOABI_optimized}.so
%{dynload_dir}/_bisect.%{SOABI_optimized}.so
%{dynload_dir}/_bz2.%{SOABI_optimized}.so
%{dynload_dir}/_codecs_cn.%{SOABI_optimized}.so
%{dynload_dir}/_codecs_hk.%{SOABI_optimized}.so
%{dynload_dir}/_codecs_iso2022.%{SOABI_optimized}.so
%{dynload_dir}/_codecs_jp.%{SOABI_optimized}.so
%{dynload_dir}/_codecs_kr.%{SOABI_optimized}.so
%{dynload_dir}/_codecs_tw.%{SOABI_optimized}.so
%{dynload_dir}/_crypt.%{SOABI_optimized}.so
%{dynload_dir}/_csv.%{SOABI_optimized}.so
%{dynload_dir}/_ctypes.%{SOABI_optimized}.so
%{dynload_dir}/_curses.%{SOABI_optimized}.so
%{dynload_dir}/_curses_panel.%{SOABI_optimized}.so
%{dynload_dir}/_dbm.%{SOABI_optimized}.so
%{dynload_dir}/_decimal.%{SOABI_optimized}.so
%{dynload_dir}/_elementtree.%{SOABI_optimized}.so
%if %{with_gdbm}
%{dynload_dir}/_gdbm.%{SOABI_optimized}.so
%endif
%{dynload_dir}/_hashlib.%{SOABI_optimized}.so
%{dynload_dir}/_heapq.%{SOABI_optimized}.so
%{dynload_dir}/_json.%{SOABI_optimized}.so
%{dynload_dir}/_lsprof.%{SOABI_optimized}.so
%{dynload_dir}/_lzma.%{SOABI_optimized}.so
%{dynload_dir}/_multibytecodec.%{SOABI_optimized}.so
%{dynload_dir}/_multiprocessing.%{SOABI_optimized}.so
%{dynload_dir}/_opcode.%{SOABI_optimized}.so
%{dynload_dir}/_pickle.%{SOABI_optimized}.so
%{dynload_dir}/_posixsubprocess.%{SOABI_optimized}.so
%{dynload_dir}/_random.%{SOABI_optimized}.so
%{dynload_dir}/_socket.%{SOABI_optimized}.so
%{dynload_dir}/_sqlite3.%{SOABI_optimized}.so
%{dynload_dir}/_ssl.%{SOABI_optimized}.so
%{dynload_dir}/_struct.%{SOABI_optimized}.so
%{dynload_dir}/array.%{SOABI_optimized}.so
%{dynload_dir}/audioop.%{SOABI_optimized}.so
%{dynload_dir}/binascii.%{SOABI_optimized}.so
%{dynload_dir}/cmath.%{SOABI_optimized}.so
%{dynload_dir}/_datetime.%{SOABI_optimized}.so
%{dynload_dir}/fcntl.%{SOABI_optimized}.so
%{dynload_dir}/grp.%{SOABI_optimized}.so
%{dynload_dir}/math.%{SOABI_optimized}.so
%{dynload_dir}/mmap.%{SOABI_optimized}.so
%{dynload_dir}/nis.%{SOABI_optimized}.so
%{dynload_dir}/ossaudiodev.%{SOABI_optimized}.so
%{dynload_dir}/parser.%{SOABI_optimized}.so
%{dynload_dir}/pyexpat.%{SOABI_optimized}.so
%{dynload_dir}/readline.%{SOABI_optimized}.so
%{dynload_dir}/resource.%{SOABI_optimized}.so
%{dynload_dir}/select.%{SOABI_optimized}.so
%{dynload_dir}/spwd.%{SOABI_optimized}.so
%{dynload_dir}/syslog.%{SOABI_optimized}.so
%{dynload_dir}/termios.%{SOABI_optimized}.so
%{dynload_dir}/_testmultiphase.%{SOABI_optimized}.so
%{dynload_dir}/unicodedata.%{SOABI_optimized}.so
%{dynload_dir}/xxlimited.%{SOABI_optimized}.so
%{dynload_dir}/zlib.%{SOABI_optimized}.so

%dir %{pylibdir}/site-packages/
%dir %{pylibdir}/site-packages/__pycache__/
%{pylibdir}/site-packages/README.txt
%{pylibdir}/*.py
%dir %{pylibdir}/__pycache__/
%{pylibdir}/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/collections/
%dir %{pylibdir}/collections/__pycache__/
%{pylibdir}/collections/*.py
%{pylibdir}/collections/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/ctypes/
%dir %{pylibdir}/ctypes/__pycache__/
%{pylibdir}/ctypes/*.py
%{pylibdir}/ctypes/__pycache__/*%{bytecode_suffixes}
%{pylibdir}/ctypes/macholib

%{pylibdir}/curses

%dir %{pylibdir}/dbm/
%dir %{pylibdir}/dbm/__pycache__/
%{pylibdir}/dbm/*.py
%{pylibdir}/dbm/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/distutils/
%dir %{pylibdir}/distutils/__pycache__/
%{pylibdir}/distutils/*.py
%{pylibdir}/distutils/__pycache__/*%{bytecode_suffixes}
%{pylibdir}/distutils/README
%{pylibdir}/distutils/command
%exclude %{pylibdir}/distutils/command/wininst-*.exe

%dir %{pylibdir}/email/
%dir %{pylibdir}/email/__pycache__/
%{pylibdir}/email/*.py
%{pylibdir}/email/__pycache__/*%{bytecode_suffixes}
%{pylibdir}/email/mime
%doc %{pylibdir}/email/architecture.rst

%{pylibdir}/encodings

%{pylibdir}/html
%{pylibdir}/http

%dir %{pylibdir}/importlib/
%dir %{pylibdir}/importlib/__pycache__/
%{pylibdir}/importlib/*.py
%{pylibdir}/importlib/__pycache__/*%{bytecode_suffixes}

%dir %{pylibdir}/json/
%dir %{pylibdir}/json/__pycache__/
%{pylibdir}/json/*.py
%{pylibdir}/json/__pycache__/*%{bytecode_suffixes}

%{pylibdir}/logging
%{pylibdir}/multiprocessing

%dir %{pylibdir}/sqlite3/
%dir %{pylibdir}/sqlite3/__pycache__/
%{pylibdir}/sqlite3/*.py
%{pylibdir}/sqlite3/__pycache__/*%{bytecode_suffixes}

%exclude %{pylibdir}/turtle.py
%exclude %{pylibdir}/__pycache__/turtle*%{bytecode_suffixes}

%{pylibdir}/urllib
%{pylibdir}/xml

%if "%{_lib}" == "lib64"
%attr(0755,root,root) %dir %{_prefix}/lib/python%{pybasever}
%attr(0755,root,root) %dir %{_prefix}/lib/python%{pybasever}/site-packages
%attr(0755,root,root) %dir %{_prefix}/lib/python%{pybasever}/site-packages/__pycache__/
%endif

# "Makefile" and the config-32/64.h file are needed by
# distutils/sysconfig.py:_init_posix(), so we include them in the core
# package, along with their parent directories (bug 531901):
%dir %{pylibdir}/config-%{LDVERSION_optimized}-%{_arch}-linux%{_gnu}/
%{pylibdir}/config-%{LDVERSION_optimized}-%{_arch}-linux%{_gnu}/Makefile
%dir %{_includedir}/python%{LDVERSION_optimized}/
%{_includedir}/python%{LDVERSION_optimized}/%{_pyconfig_h}

%{_libdir}/%{py_INSTSONAME_optimized}
%{_libdir}/libpython3.so.%{scl}
%if 0%{?with_systemtap}
%{?scl:%dir %{_datadir}/tapsetdir}
%{?scl:%dir %{tapsetdir}}
%{tapsetdir}/%{libpython_stp_optimized}
%doc systemtap-example.stp pyfuntop.stp
%endif

%files devel
%defattr(-,root,root)
%{?scl:%{_root_prefix}/lib/rpm/pythondeps-scl-36.sh}
%{?scl:%{_root_prefix}/lib/rpm/redhat/brp-python-bytecompile-with-scl-python-36}
%{pylibdir}/config-%{LDVERSION_optimized}-%{_arch}-linux%{_gnu}/*
%exclude %{pylibdir}/config-%{LDVERSION_optimized}-%{_arch}-linux%{_gnu}/Makefile
%{pylibdir}/distutils/command/wininst-*.exe
%{_includedir}/python%{LDVERSION_optimized}/*.h
%exclude %{_includedir}/python%{LDVERSION_optimized}/%{_pyconfig_h}
%doc Misc/README.valgrind Misc/valgrind-python.supp Misc/gdbinit
%{_bindir}/python-config
%{_bindir}/python3-config
%{_bindir}/python%{pybasever}-config
%{_bindir}/python%{LDVERSION_optimized}-config
%{_bindir}/python%{LDVERSION_optimized}-*-config
%{_libdir}/libpython%{LDVERSION_optimized}.so
%{?scl:%dir %{_libdir}/pkgconfig}
%{_libdir}/pkgconfig/python-%{LDVERSION_optimized}.pc
%{_libdir}/pkgconfig/python-%{pybasever}.pc
%{_libdir}/pkgconfig/python.pc
%{_libdir}/pkgconfig/python3.pc
%config(noreplace) %{?scl:%_root_sysconfdir}%{!?scl:%_sysconfdir}/rpm/macros.python3%{?scl:.%{scl}}
%config(noreplace) %{?scl:%_root_sysconfdir}%{!?scl:%_sysconfdir}/rpm/macros.pybytecompile%{?scl:.%{scl}}

%files tools
%defattr(-,root,root,755)
%{_bindir}/python3-2to3
%{_bindir}/python-2to3
%{_bindir}/2to3-%{pybasever}
%{_bindir}/2to3
%{_bindir}/idle*
%{_bindir}/pynche
%{pylibdir}/Tools
%doc %{pylibdir}/Doc

%files tkinter
%defattr(-,root,root,755)
%{pylibdir}/tkinter
%exclude %{pylibdir}/tkinter/test
%{dynload_dir}/_tkinter.%{SOABI_optimized}.so
%{pylibdir}/turtle.py
%{pylibdir}/__pycache__/turtle*%{bytecode_suffixes}
%dir %{pylibdir}/turtledemo
%{pylibdir}/turtledemo/*.py
%{pylibdir}/turtledemo/*.cfg
%dir %{pylibdir}/turtledemo/__pycache__/
%{pylibdir}/turtledemo/__pycache__/*%{bytecode_suffixes}

%files test
%defattr(-, root, root)
%{pylibdir}/ctypes/test
%{pylibdir}/distutils/tests
%{pylibdir}/sqlite3/test
%{pylibdir}/test
%{dynload_dir}/_ctypes_test.%{SOABI_optimized}.so
%{dynload_dir}/_testbuffer.%{SOABI_optimized}.so
%{dynload_dir}/_testcapi.%{SOABI_optimized}.so
%{dynload_dir}/_testimportmultiple.%{SOABI_optimized}.so
%{pylibdir}/lib2to3/tests
%{pylibdir}/tkinter/test
%{pylibdir}/unittest/test


# We don't bother splitting the debug build out into further subpackages:
# if you need it, you're probably a developer.

# Hence the manifest is the combination of analogous files in the manifests of
# all of the other subpackages

%if 0%{?with_debug_build}
%files debug
%defattr(-,root,root,-)

# Analog of the core subpackage's files:
%{_bindir}/python%{LDVERSION_debug}
%{_bindir}/python-debug
%{_bindir}/python3-debug

# Analog of the -libs subpackage's files:
# ...with debug builds of the built-in "extension" modules:

%{dynload_dir}/_blake2.%{SOABI_debug}.so
%{dynload_dir}/_sha3.%{SOABI_debug}.so

%{dynload_dir}/_asyncio.%{SOABI_debug}.so
%{dynload_dir}/_bisect.%{SOABI_debug}.so
%{dynload_dir}/_bz2.%{SOABI_debug}.so
%{dynload_dir}/_codecs_cn.%{SOABI_debug}.so
%{dynload_dir}/_codecs_hk.%{SOABI_debug}.so
%{dynload_dir}/_codecs_iso2022.%{SOABI_debug}.so
%{dynload_dir}/_codecs_jp.%{SOABI_debug}.so
%{dynload_dir}/_codecs_kr.%{SOABI_debug}.so
%{dynload_dir}/_codecs_tw.%{SOABI_debug}.so
%{dynload_dir}/_crypt.%{SOABI_debug}.so
%{dynload_dir}/_csv.%{SOABI_debug}.so
%{dynload_dir}/_ctypes.%{SOABI_debug}.so
%{dynload_dir}/_curses.%{SOABI_debug}.so
%{dynload_dir}/_curses_panel.%{SOABI_debug}.so
%{dynload_dir}/_dbm.%{SOABI_debug}.so
%{dynload_dir}/_decimal.%{SOABI_debug}.so
%{dynload_dir}/_elementtree.%{SOABI_debug}.so
%if %{with_gdbm}
%{dynload_dir}/_gdbm.%{SOABI_debug}.so
%endif
%{dynload_dir}/_hashlib.%{SOABI_debug}.so
%{dynload_dir}/_heapq.%{SOABI_debug}.so
%{dynload_dir}/_json.%{SOABI_debug}.so
%{dynload_dir}/_lsprof.%{SOABI_debug}.so
%{dynload_dir}/_lzma.%{SOABI_debug}.so
%{dynload_dir}/_multibytecodec.%{SOABI_debug}.so
%{dynload_dir}/_multiprocessing.%{SOABI_debug}.so
%{dynload_dir}/_opcode.%{SOABI_debug}.so
%{dynload_dir}/_pickle.%{SOABI_debug}.so
%{dynload_dir}/_posixsubprocess.%{SOABI_debug}.so
%{dynload_dir}/_random.%{SOABI_debug}.so
%{dynload_dir}/_socket.%{SOABI_debug}.so
%{dynload_dir}/_sqlite3.%{SOABI_debug}.so
%{dynload_dir}/_ssl.%{SOABI_debug}.so
%{dynload_dir}/_struct.%{SOABI_debug}.so
%{dynload_dir}/array.%{SOABI_debug}.so
%{dynload_dir}/audioop.%{SOABI_debug}.so
%{dynload_dir}/binascii.%{SOABI_debug}.so
%{dynload_dir}/cmath.%{SOABI_debug}.so
%{dynload_dir}/_datetime.%{SOABI_debug}.so
%{dynload_dir}/fcntl.%{SOABI_debug}.so
%{dynload_dir}/grp.%{SOABI_debug}.so
%{dynload_dir}/math.%{SOABI_debug}.so
%{dynload_dir}/mmap.%{SOABI_debug}.so
%{dynload_dir}/nis.%{SOABI_debug}.so
%{dynload_dir}/ossaudiodev.%{SOABI_debug}.so
%{dynload_dir}/parser.%{SOABI_debug}.so
%{dynload_dir}/pyexpat.%{SOABI_debug}.so
%{dynload_dir}/readline.%{SOABI_debug}.so
%{dynload_dir}/resource.%{SOABI_debug}.so
%{dynload_dir}/select.%{SOABI_debug}.so
%{dynload_dir}/spwd.%{SOABI_debug}.so
%{dynload_dir}/syslog.%{SOABI_debug}.so
%{dynload_dir}/termios.%{SOABI_debug}.so
%{dynload_dir}/_testmultiphase.%{SOABI_debug}.so
%{dynload_dir}/unicodedata.%{SOABI_debug}.so
%{dynload_dir}/zlib.%{SOABI_debug}.so

# No need to split things out the "Makefile" and the config-32/64.h file as we
# do for the regular build above (bug 531901), since they're all in one package
# now; they're listed below, under "-devel":

%{_libdir}/%{py_INSTSONAME_debug}
%if 0%{?with_systemtap}
%dir %(dirname %{tapsetdir})
%dir %{tapsetdir}
%{tapsetdir}/%{libpython_stp_debug}
%endif

# Analog of the -devel subpackage's files:
%{pylibdir}/config-%{LDVERSION_debug}-%{_arch}-linux%{_gnu}
%{_includedir}/python%{LDVERSION_debug}
%{_bindir}/python%{LDVERSION_debug}-config
%{_bindir}/python%{LDVERSION_debug}-*-config
%{_libdir}/libpython%{LDVERSION_debug}.so
%{_libdir}/pkgconfig/python-%{LDVERSION_debug}.pc

# Analog of the -tools subpackage's files:
#  None for now; we could build precanned versions that have the appropriate
# shebang if needed

# Analog  of the tkinter subpackage's files:
%{dynload_dir}/_tkinter.%{SOABI_debug}.so

# Analog  of the -test subpackage's files:
%{dynload_dir}/_ctypes_test.%{SOABI_debug}.so
%{dynload_dir}/_testbuffer.%{SOABI_debug}.so
%{dynload_dir}/_testcapi.%{SOABI_debug}.so
%{dynload_dir}/_testimportmultiple.%{SOABI_debug}.so

%endif # with_debug_build

# We put the debug-gdb.py file inside /usr/lib/debug to avoid noise from
# ldconfig (rhbz:562980).
#
# The /usr/lib/rpm/redhat/macros defines %%__debug_package to use
# debugfiles.list, and it appears that everything below /usr/lib/debug and
# (/usr/src/debug) gets added to this file (via LISTFILES) in
# /usr/lib/rpm/find-debuginfo.sh
#
# Hence by installing it below /usr/lib/debug we ensure it is added to the
# -debuginfo subpackage
# (if it doesn't, then the rpmbuild ought to fail since the debug-gdb.py
# payload file would be unpackaged)


# ======================================================
# Finally, the changelog:
# ======================================================

%changelog
* Tue Jan 09 2018 Charalampos Stratakis <cstratak@redhat.com> - 3.6.3-3
- Bump release for rebuild

* Mon Jan 08 2018 Charalampos Stratakis <cstratak@redhat.com> - 3.6.3-2
- Fix conditional logic in the hashlib patch.
Resolves: rhbz#1532663

* Thu Oct 05 2017 Charalampos Stratakis <cstratak@redhat.com> - 3.6.3-1
- Update to Python 3.6.3
Resolves: rhbz#1498526

* Mon Aug 07 2017 Iryna Shcherbina <ishcherb@redhat.com> - 3.6.2-3
- Fix the "urllib FTP protocol stream injection" vulnerability
Resolves: rhbz#1478955

* Fri Aug 04 2017 Tomas Orsava <torsava@redhat.com> - 3.6.2-2
- Hard-code RUNPATH (not RPATH) into the executables and C libraries so that
  Python can be run without first running scl enable
Resolves: rhbz#1479406

* Wed Aug 2 2017 Iryna Shcherbina <ishcherb@redhat.com> - 3.6.2-1
- Update to Python 3.6.2
- Enable profile guided optimizations for x86_64 and i686 architectures
- Replace the "--verbose" flag with "-wW" and add "--slowest" flag
Resolves: rhbz#1463715

* Tue Aug 1 2017 Iryna Shcherbina <ishcherb@redhat.com> - 3.6.1-3
- Make test_asyncio not depend on the current SIGHUP signal handler
Resolves: rhbz#1461453

* Wed Jun 14 2017 Charalampos Stratakis <cstratak@redhat.com> - 3.6.1-2
- Enable rewheel

* Tue Jun 06 2017 Charalampos Stratakis <cstratak@redhat.com> - 3.6.1-1
- Update to Python 3.6.1
- Disable rewheel mode

* Fri Mar 17 2017 Tomas Orsava <torsava@redhat.com> - 3.5.1-12
- Moved pythondeps-scl-35.sh and 2 macro definitions from the rh-python35-build
  subpackage here to the python-devel subpackage where it should be for
  dependant collections to build properly
- Also defined the 2 macros in this spec file so they are available during the
  build of Python itself
Resolves: rhbz#1422346

* Wed Sep 14 2016 Tomas Orsava <torsava@redhat.com> - 3.5.1-11
- Updated .pyc 'bytecompilation with the newly installed interpreter' to also
  recompile optimized .pyc files
- Removed .pyo 'bytecompilation with the newly installed interpreter', as .pyo
  files are no more
- Updated %py_byte_compile macro
Resolves rhbz#1374667

* Fri Aug 05 2016 Charalampos Stratakis <cstratak@redhat.com> - 3.5.1-10
- Bump release number for rebuild
Resolves: rhbz#1359174

* Fri Aug 05 2016 Charalampos Stratakis <cstratak@redhat.com> - 3.5.1-8
- Fix for CVE-2016-1000110 HTTPoxy attack
Resolves: rhbz#1359174

* Tue Jun 21 2016 Tomas Orsava <torsava@redhat.com> - 3.5.1-7
- Fix for CVE-2016-0772 python: smtplib StartTLS stripping attack (rhbz#1303647)
  Raise an error when STARTTLS fails (upstream patch)
Resolves: rhbz#1346361

* Tue Apr 26 2016 Charalampos Stratakis <cstratak@redhat.com> - 3.5.1-6
- Modify cprofile-sort-option.patch for Python 3
Resolves: rhbz#1326287

* Thu Apr 14 2016 Charalampos Stratakis <cstratak@redhat.com> - 3.5.1-5
- Add choices for sort option of cProfile for better output
Resolves: rhbz#1326287

* Wed Feb 17 2016 Robert Kuska <rkuska@redhat.com> - 3.5.1-4
- Properly apply patches 170&201, remove duplicated Patch200(207)

* Sat Feb 13 2016 Robert Kuska <rkuska@redhat.com> - 3.5.1-3
- Rebuild with rewheel, enable tests

* Sat Feb 13 2016 Robert Kuska <rkuska@redhat.com> - 3.5.1-2
- Fix bytecompile macro name in macros.python3
- Temporary disable tests for faster rebuild

* Thu Feb 11 2016 Robert Kuska <rkuska@redhat.com> - 3.5.1-1
- Update to 3.5.1

* Tue Nov 24 2015 Robert Kuska <rkuska@redhat.com> - 3.5.0-6
- Build python3 for scl

* Sun Nov 15 2015 Robert Kuska <rkuska@redhat.com> - 3.5.0-5
- Remove versioned libpython from devel package

* Fri Nov 13 2015 Than Ngo <than@redhat.com> 3.5.0-4
- add correct arch for ppc64/ppc64le to fix build failure

* Wed Nov 11 2015 Robert Kuska <rkuska@redhat.com> - 3.5.0-3
- Hide the private _Py_atomic_xxx symbols from public header

* Wed Oct 14 2015 Robert Kuska <rkuska@redhat.com> - 3.5.0-2
- Rebuild with wheel set to 1

* Tue Sep 15 2015 Matej Stuchlik <mstuchli@redhat.com> - 3.5.0-1
- Update to 3.5.0

* Mon Jun 29 2015 Thomas Spura <tomspur@fedoraproject.org> - 3.4.3-4
- python3-devel: Require python-macros for version independant macros such as
  python_provide. See fpc#281 and fpc#534.

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Jun 17 2015 Matej Stuchlik <mstuchli@redhat.com> - 3.4.3-4
- Use 1024bit DH key in test_ssl
- Use -O0 when compiling -debug build
- Update pip version variable to the version we actually ship

* Wed Jun 17 2015 Matej Stuchlik <mstuchli@redhat.com> - 3.4.3-3
- Make relocating Python by changing _prefix actually work
Resolves: rhbz#1231801

* Mon May  4 2015 Peter Robinson <pbrobinson@fedoraproject.org> 3.4.3-2
- Disable test_gdb on aarch64 (rhbz#1196181), it joins all other non x86 arches

* Thu Mar 12 2015 Matej Stuchlik <mstuchli@redhat.com> - 3.4.3-1
- Updated to 3.4.3
- BuildPython now accepts additional build options
- Temporarily disabled test_gdb on arm (rhbz#1196181)

* Wed Feb 25 2015 Matej Stuchlik <mstuchli@redhat.com> - 3.4.2-7
- Fixed undefined behaviour in faulthandler which caused test to hang on x86_64
  (http://bugs.python.org/issue23433)

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 3.4.2-6
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Tue Feb 17 2015 Ville Skyttä <ville.skytta@iki.fi> - 3.4.2-5
- Own systemtap dirs (#710733)

* Mon Jan 12 2015 Dan Horák <dan[at]danny.cz> - 3.4.2-4
- build with valgrind on ppc64le
- disable test_gdb on s390(x) until rhbz#1181034 is resolved

* Tue Dec 16 2014 Robert Kuska <rkuska@redhat.com> - 3.4.2-3
- New patches: 170 (gc asserts), 200 (gettext headers),
  201 (gdbm memory leak)

* Thu Dec 11 2014 Robert Kuska <rkuska@redhat.com> - 3.4.2-2
- OpenSSL disabled SSLv3 in SSLv23 method

* Thu Nov 13 2014 Matej Stuchlik <mstuchli@redhat.com> - 3.4.2-1
- Update to 3.4.2
- Refreshed patches: 156 (gdb autoload)
- Removed: 195 (Werror declaration), 197 (CVE-2014-4650)

* Mon Nov 03 2014 Slavek Kabrda <bkabrda@redhat.com> - 3.4.1-16
- Fix CVE-2014-4650 - CGIHTTPServer URL handling
Resolves: rhbz#1113529

* Sun Sep 07 2014 Karsten Hopp <karsten@redhat.com> 3.4.1-15
- exclude test_gdb on ppc* (rhbz#1132488)

* Thu Aug 21 2014 Slavek Kabrda <bkabrda@redhat.com> - 3.4.1-14
- Update rewheel patch with fix from https://github.com/bkabrda/rewheel/pull/1

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun  8 2014 Peter Robinson <pbrobinson@fedoraproject.org> 3.4.1-12
- aarch64 has valgrind, just list those that don't support it

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.1-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Jun 04 2014 Karsten Hopp <karsten@redhat.com> 3.4.1-10
- bump release and rebuild to link with the correct tcl/tk libs on ppcle

* Tue Jun 03 2014 Matej Stuchlik <mstuchli@redhat.com> - 3.4.1-9
- Change paths to bundled projects in rewheel patch

* Fri May 30 2014 Miro Hrončok <mhroncok@redhat.com> - 3.4.1-8
- In config script, use uname -m to write the arch

* Thu May 29 2014 Dan Horák <dan[at]danny.cz> - 3.4.1-7
- update the arch list where valgrind exists - %%power64 includes also
    ppc64le which is not supported yet

* Thu May 29 2014 Miro Hrončok <mhroncok@redhat.com> - 3.4.1-6
- Forward arguments to the arch specific config script
Resolves: rhbz#1102683

* Wed May 28 2014 Miro Hrončok <mhroncok@redhat.com> - 3.4.1-5
- Rename python3.Xm-config script to arch specific.
Resolves: rhbz#1091815

* Tue May 27 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 3.4.1-4
- Use python3-*, not python-* runtime requires on setuptools and pip
- rebuild for tcl-8.6

* Tue May 27 2014 Matej Stuchlik <mstuchli@redhat.com> - 3.4.1-3
- Update the rewheel module

* Mon May 26 2014 Miro Hrončok <mhroncok@redhat.com> - 3.4.1-2
- Fix multilib dependencies.
Resolves: rhbz#1091815

* Sun May 25 2014 Matej Stuchlik <mstuchli@redhat.com> - 3.4.1-1
- Update to Python 3.4.1

* Sun May 25 2014 Matej Stuchlik <mstuchli@redhat.com> - 3.4.0-8
- Fix test_gdb failure on ppc64le
Resolves: rhbz#1095355

* Thu May 22 2014 Miro Hrončok <mhroncok@redhat.com> - 3.4.0-7
- Add macro %%python3_version_nodots

* Sun May 18 2014 Matej Stuchlik <mstuchli@redhat.com> - 3.4.0-6
- Disable test_faulthandler, test_gdb on aarch64
Resolves: rhbz#1045193

* Fri May 16 2014 Matej Stuchlik <mstuchli@redhat.com> - 3.4.0-5
- Don't add Werror=declaration-after-statement for extension
  modules through setup.py (PyBT#21121)

* Mon May 12 2014 Matej Stuchlik <mstuchli@redhat.com> - 3.4.0-4
- Add setuptools and pip to Requires

* Tue Apr 29 2014 Matej Stuchlik <mstuchli@redhat.com> - 3.4.0-3
- Point __os_install_post to correct brp-* files

* Tue Apr 15 2014 Matej Stuchlik <mstuchli@redhat.com> - 3.4.0-2
- Temporarily disable tests requiring SIGHUP (rhbz#1088233)

* Tue Apr 15 2014 Matej Stuchlik <mstuchli@redhat.com> - 3.4.0-1
- Update to Python 3.4 final
- Add patch adding the rewheel module
- Merge patches from master

* Wed Jan 08 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 3.4.0-0.1.b2
- Update to Python 3.4 beta 2.
- Refreshed patches: 55 (systemtap), 146 (hashlib-fips), 154 (test_gdb noise)
- Dropped patches: 114 (statvfs constants), 177 (platform unicode)

* Mon Nov 25 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 3.4.0-0.1.b1
- Update to Python 3.4 beta 1.
- Refreshed patches: 102 (lib64), 111 (no static lib), 125 (less verbose COUNT
ALLOCS), 141 (fix COUNT_ALLOCS in test_module), 146 (hashlib fips),
157 (UID+GID overflows), 173 (ENOPROTOOPT in bind_port)
- Removed patch 00187 (remove pthread atfork; upstreamed)

* Mon Nov 04 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 3.4.0-0.1.a4
- Update to Python 3.4 alpha 4.
- Refreshed patches: 55 (systemtap), 102 (lib64), 111 (no static lib),
114 (statvfs flags), 132 (unittest rpmbuild hooks), 134 (fix COUNT_ALLOCS in
test_sys), 143 (tsc on ppc64), 146 (hashlib fips), 153 (test gdb noise),
157 (UID+GID overflows), 173 (ENOPROTOOPT in bind_port), 186 (dont raise
from py_compile)
- Removed patches: 129 (test_subprocess nonreadable dir - no longer fails in
Koji), 142 (the mock issue that caused this is fixed)
- Added patch 187 (remove thread atfork) - will be in next version
- Refreshed script for checking pyc and pyo timestamps with new ignored files.
- The fips patch is disabled for now until upstream makes a final decision
what to do with sha3 implementation for 3.4.0.

* Wed Oct 30 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 3.3.2-7
- Bytecompile all *.py files properly during build (rhbz#1023607)

* Fri Aug 23 2013 Matej Stuchlik <mstuchli@redhat.com> - 3.3.2-6
- Added fix for CVE-2013-4238 (rhbz#996399)

* Fri Jul 26 2013 Dennis Gilmore <dennis@ausil.us> - 3.3.2-5
- fix up indentation in arm patch

* Fri Jul 26 2013 Dennis Gilmore <dennis@ausil.us> - 3.3.2-4
- disable a test that fails on arm
- enable valgrind support on arm arches

* Tue Jul 02 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 3.3.2-3
- Fix build with libffi containing multilib wrapper for ffi.h (rhbz#979696).

* Mon May 20 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 3.3.2-2
- Add patch for CVE-2013-2099 (rhbz#963261).

* Thu May 16 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 3.3.2-1
- Updated to Python 3.3.2.
- Refreshed patches: 153 (gdb test noise)
- Dropped patches: 175 (configure -Wformat, fixed upstream), 182 (gdb
test threads)
- Synced patch numbers with python.spec.

* Thu May  9 2013 David Malcolm <dmalcolm@redhat.com> - 3.3.1-4
- fix test.test_gdb.PyBtTests.test_threads on ppc64 (patch 181; rhbz#960010)

* Thu May 02 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 3.3.1-3
- Add patch that enables building on ppc64p7 (replace the sed, so that
we get consistent with python2 spec and it's more obvious that we're doing it.

* Wed Apr 24 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 3.3.1-2
- Add fix for gdb tests failing on arm, rhbz#951802.

* Tue Apr 09 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 3.3.1-1
- Updated to Python 3.3.1.
- Refreshed patches: 55 (systemtap), 111 (no static lib), 146 (hashlib fips),
153 (fix test_gdb noise), 157 (uid, gid overflow - fixed upstream, just
keeping few more downstream tests)
- Removed patches: 3 (audiotest.au made it to upstream tarball)
- Removed workaround for http://bugs.python.org/issue14774, discussed in
http://bugs.python.org/issue15298 and fixed in revision 24d52d3060e8.

* Mon Mar 25 2013 David Malcolm <dmalcolm@redhat.com> - 3.3.0-10
- fix gcc 4.8 incompatibility (rhbz#927358); regenerate autotool intermediates

* Mon Mar 25 2013 David Malcolm <dmalcolm@redhat.com> - 3.3.0-9
- renumber patches to keep them in sync with python.spec

* Fri Mar 15 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 3.3.0-8
- Fix error in platform.platform() when non-ascii byte strings are decoded to
  unicode (rhbz#922149)

* Thu Mar 14 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 3.3.0-7
- Fix up shared library extension (rhbz#889784)

* Thu Mar 07 2013 Karsten Hopp <karsten@redhat.com> 3.3.0-6
- add ppc64p7 build target, optimized for Power7

* Mon Mar  4 2013 David Malcolm <dmalcolm@redhat.com> - 3.3.0-5
- add workaround for ENOPROTOOPT seen running selftests in Koji
(rhbz#913732)

* Mon Mar  4 2013 David Malcolm <dmalcolm@redhat.com> - 3.3.0-4
- remove config flag from /etc/rpm/macros.{python3|pybytecompile}

* Mon Feb 11 2013 David Malcolm <dmalcolm@redhat.com> - 3.3.0-3
- add aarch64 (rhbz#909783)

* Thu Nov 29 2012 David Malcolm <dmalcolm@redhat.com> - 3.3.0-2
- add BR on bluez-libs-devel (rhbz#879720)

* Sat Sep 29 2012 David Malcolm <dmalcolm@redhat.com> - 3.3.0-1
- 3.3.0rc3 -> 3.3.0; drop alphatag

* Mon Sep 24 2012 David Malcolm <dmalcolm@redhat.com> - 3.3.0-0.6.rc3
- 3.3.0rc2 -> 3.3.0rc3

* Mon Sep 10 2012 David Malcolm <dmalcolm@redhat.com> - 3.3.0-0.5.rc2
- 3.3.0rc1 -> 3.3.0rc2; refresh patch 55

* Mon Aug 27 2012 David Malcolm <dmalcolm@redhat.com> - 3.3.0-0.4.rc1
- 3.3.0b2 -> 3.3.0rc1; refresh patches 3, 55

* Mon Aug 13 2012 David Malcolm <dmalcolm@redhat.com> - 3.3.0-0.3.b2
- 3.3b1 -> 3.3b2; drop upstreamed patch 152; refresh patches 3, 102, 111,
134, 153, 160; regenenerate autotools patch; rework systemtap patch to work
correctly when LANG=C (patch 55); importlib.test was moved to
test.test_importlib upstream

* Mon Aug 13 2012 Karsten Hopp <karsten@redhat.com> 3.3.0-0.2.b1
- disable some failing checks on PPC* (rhbz#846849)

* Fri Aug  3 2012 David Malcolm <dmalcolm@redhat.com> - 3.3.0-0.1.b1
- 3.2 -> 3.3: https://fedoraproject.org/wiki/Features/Python_3.3
- 3.3.0b1: refresh patches 3, 55, 102, 111, 113, 114, 134, 157; drop upstream
patch 147; regenenerate autotools patch; drop "--with-wide-unicode" from
configure (PEP 393); "plat-linux2" -> "plat-linux" (upstream issue 12326);
"bz2" -> "_bz2" and "crypt" -> "_crypt"; egg-info files are no longer shipped
for stdlib (upstream issues 10645 and 12218); email/test moved to
test/test_email; add /usr/bin/pyvenv[-3.3] and venv module (PEP 405); add
_decimal and _lzma modules; make collections modules explicit in payload again
(upstream issue 11085); add _testbuffer module to tests subpackage (added in
upstream commit 3f9b3b6f7ff0); fix test failures (patches 160 and 161);
workaround erroneously shared _sysconfigdata.py upstream issue #14774; fix
distutils.sysconfig traceback (patch 162); add BuildRequires: xz-devel (for
_lzma module); skip some tests within test_socket (patch 163)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.3-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul 20 2012 David Malcolm <dmalcolm@redhat.com> - 3.3.0-0.1.b1

* Fri Jun 22 2012 David Malcolm <dmalcolm@redhat.com> - 3.2.3-10
- use macro for power64 (rhbz#834653)

* Mon Jun 18 2012 David Malcolm <dmalcolm@redhat.com> - 3.2.3-9
- fix missing include in uid/gid handling patch (patch 157; rhbz#830405)

* Wed May 30 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 3.2.3-8
- fix tapset for debug build

* Tue May 15 2012 David Malcolm <dmalcolm@redhat.com> - 3.2.3-7
- update uid/gid handling to avoid int overflows seen with uid/gid
values >= 2^31 on 32-bit architectures (patch 157; rhbz#697470)

* Fri May  4 2012 David Malcolm <dmalcolm@redhat.com> - 3.2.3-6
- renumber autotools patch from 300 to 5000
- specfile cleanups

* Mon Apr 30 2012 David Malcolm <dmalcolm@redhat.com> - 3.2.3-5
- fix test_gdb.py (patch 156; rhbz#817072)

* Fri Apr 20 2012 David Malcolm <dmalcolm@redhat.com> - 3.2.3-4
- avoid allocating thunks in ctypes unless absolutely necessary, to avoid
generating SELinux denials on "import ctypes" and "import uuid" when embedding
Python within httpd (patch 155; rhbz#814391)

* Fri Apr 20 2012 David Malcolm <dmalcolm@redhat.com> - 3.2.3-3
- add explicit version requirements on expat to avoid linkage problems with
XML_SetHashSalt

* Thu Apr 12 2012 David Malcolm <dmalcolm@redhat.com> - 3.2.3-2
- fix test_gdb (patch 153)

* Wed Apr 11 2012 David Malcolm <dmalcolm@redhat.com> - 3.2.3-1
- 3.2.3; refresh patch 102 (lib64); drop upstream patches 148 (gdbm magic
values), 149 (__pycache__ fix); add patch 152 (test_gdb regex)

* Thu Feb  9 2012 Thomas Spura <tomspur@fedoraproject.org> - 3.2.2-13
- use newly installed python for byte compiling (now for real)

* Sun Feb  5 2012 Thomas Spura <tomspur@fedoraproject.org> - 3.2.2-12
- use newly installed python for byte compiling (#787498)

* Wed Jan  4 2012 Ville Skyttä <ville.skytta@iki.fi> - 3.2.2-11
- Build with $RPM_LD_FLAGS (#756863).
- Use xz-compressed source tarball.

* Wed Dec 07 2011 Karsten Hopp <karsten@redhat.com> 3.2.2-10
- disable rAssertAlmostEqual in test_cmath on PPC (#750811)

* Mon Oct 17 2011 Rex Dieter <rdieter@fedoraproject.org> - 3.2.2-9
- python3-devel missing autogenerated pkgconfig() provides (#746751)

* Mon Oct 10 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.2-8
- cherrypick fix for distutils not using __pycache__ when byte-compiling
files (rhbz#722578)

* Fri Sep 30 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.2-7
- re-enable gdbm (patch 148; rhbz#742242)

* Fri Sep 16 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.2-6
- add a sys._debugmallocstats() function (patch 147)

* Wed Sep 14 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.2-5
- support OpenSSL FIPS mode in _hashlib and hashlib; don't build the _md5 and
_sha* modules, relying on _hashlib in hashlib (rhbz#563986; patch 146)

* Tue Sep 13 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.2-4
- disable gdbm module to prepare for gdbm soname bump

* Mon Sep 12 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.2-3
- renumber and rename patches for consistency with python.spec (8 to 55, 106
to 104, 6 to 111, 104 to 113, 105 to 114, 125, 131, 130 to 143)

* Sat Sep 10 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.2-2
- rewrite of "check", introducing downstream-only hooks for skipping specific
cases in an rpmbuild (patch 132), and fixing/skipping failing tests in a more
fine-grained manner than before; (patches 106, 133-142 sparsely, moving
patches for consistency with python.spec: 128 to 134, 126 to 135, 127 to 141)

* Tue Sep  6 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.2-1
- 3.2.2

* Thu Sep  1 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.1-7
- run selftests with "--verbose"
- disable parts of test_io on ppc (rhbz#732998)

* Wed Aug 31 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.1-6
- use "--findleaks --verbose3" when running test suite

* Tue Aug 23 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.1-5
- re-enable and fix the --with-tsc option on ppc64, and rework it on 32-bit
ppc to avoid aliasing violations (patch 130; rhbz#698726)

* Tue Aug 23 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.1-4
- don't use --with-tsc on ppc64 debug builds (rhbz#698726)

* Thu Aug 18 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.1-3
- add %%python3_version to the rpm macros (rhbz#719082)

* Mon Jul 11 2011 Dennis Gilmore <dennis@ausil.us> - 3.2.1-2
- disable some tests on sparc arches

* Mon Jul 11 2011 David Malcolm <dmalcolm@redhat.com> - 3.2.1-1
- 3.2.1; refresh lib64 patch (102), subprocess unit test patch (129), disabling
of static library build (due to Modules/_testembed; patch 6), autotool
intermediates (patch 300)

* Fri Jul  8 2011 David Malcolm <dmalcolm@redhat.com> - 3.2-5
- use the gdb hooks from the upstream tarball, rather than keeping our own copy

* Fri Jul  8 2011 David Malcolm <dmalcolm@redhat.com> - 3.2-4
- don't run test_openpty and test_pty in %%check

* Fri Jul  8 2011 David Malcolm <dmalcolm@redhat.com> - 3.2-3
- cleanup of BuildRequires; add comment headings to specfile sections

* Tue Apr 19 2011 David Malcolm <dmalcolm@redhat.com> - 3.2-2
- fix the libpython.stp systemtap tapset (rhbz#697730)

* Mon Feb 21 2011 David Malcolm <dmalcolm@redhat.com> - 3.2-1
- 3.2
- drop alphatag
- regenerate autotool patch

* Mon Feb 14 2011 David Malcolm <dmalcolm@redhat.com> - 3.2-0.13.rc3
- add a /usr/bin/python3-debug symlink within the debug subpackage

* Mon Feb 14 2011 David Malcolm <dmalcolm@redhat.com> - 3.2-0.12.rc3
- 3.2rc3
- regenerate autotool patch

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2-0.11.rc2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 31 2011 David Malcolm <dmalcolm@redhat.com> - 3.2-0.10.rc2
- 3.2rc2

* Mon Jan 17 2011 David Malcolm <dmalcolm@redhat.com> - 3.2-0.9.rc1
- 3.2rc1
- rework patch 6 (static lib removal)
- remove upstreamed patch 130 (ppc debug build)
- regenerate patch 300 (autotool intermediates)
- updated packaging to reflect upstream rewrite of "Demo" (issue 7962)
- added libpython3.so and 2to3-3.2

* Wed Jan  5 2011 David Malcolm <dmalcolm@redhat.com> - 3.2-0.8.b2
- set EXTRA_CFLAGS to our CFLAGS, rather than overriding OPT, fixing a linker
error with dynamic annotations (when configured using --with-valgrind)
- fix the ppc build of the debug configuration (patch 130; rhbz#661510)

* Tue Jan  4 2011 David Malcolm <dmalcolm@redhat.com> - 3.2-0.7.b2
- add --with-valgrind to configuration (on architectures that support this)

* Wed Dec 29 2010 David Malcolm <dmalcolm@redhat.com> - 3.2-0.6.b2
- work around test_subprocess failure seen in koji (patch 129)

* Tue Dec 28 2010 David Malcolm <dmalcolm@redhat.com> - 3.2-0.5.b2
- 3.2b2
- rework patch 3 (removal of mimeaudio tests), patch 6 (no static libs),
patch 8 (systemtap), patch 102 (lib64)
- remove patch 4 (rendered redundant by upstream r85537), patch 103 (PEP 3149),
patch 110 (upstreamed expat fix), patch 111 (parallel build fix for grammar
fixed upstream)
- regenerate patch 300 (autotool intermediates)
- workaround COUNT_ALLOCS weakref issues in test suite (patch 126, patch 127,
patch 128)
- stop using runtest.sh in %%check (dropped by upstream), replacing with
regrtest; fixup list of failing tests
- introduce "pyshortver", "SOABI_optimized" and "SOABI_debug" macros
- rework manifests of shared libraries to use "SOABI_" macros, reflecting
PEP 3149
- drop itertools, operator and _collections modules from the manifests as py3k
commit r84058 moved these inside libpython; json/tests moved to test/json_tests
- move turtle code into the tkinter subpackage

* Wed Nov 17 2010 David Malcolm <dmalcolm@redhat.com> - 3.2-0.5.a1
- fix sysconfig to not rely on the -devel subpackage (rhbz#653058)

* Thu Sep  9 2010 David Malcolm <dmalcolm@redhat.com> - 3.2-0.4.a1
- move most of the content of the core package to the libs subpackage, given
that the libs aren't meaningfully usable without the standard libraries

* Wed Sep  8 2010 David Malcolm <dmalcolm@redhat.com> - 3.2-0.3.a1
- Move test.support to core package (rhbz#596258)
- Add various missing __pycache__ directories to payload

* Sun Aug 22 2010 Toshio Kuratomi <toshio@fedoraproject.org> - 3.2-0.2.a1
- Add __pycache__ directory for site-packages

* Sun Aug 22 2010 Thomas Spura <tomspur@fedoraproject.org> - 3.2-0.1.a1
- on 64bit "stdlib" was still "/usr/lib/python*" (modify *lib64.patch)
- make find-provides-without-python-sonames.sh 64bit aware

* Sat Aug 21 2010 David Malcolm <dmalcolm@redhat.com> - 3.2-0.0.a1
- 3.2a1; add alphatag
- rework %%files in the light of PEP 3147 (__pycache__)
- drop our configuration patch to Setup.dist (patch 0): setup.py should do a
better job of things, and the %%files explicitly lists our modules (r82746
appears to break the old way of doing things).  This leads to various modules
changing from "foomodule.so" to "foo.so".  It also leads to the optimized build
dropping the _sha1, _sha256 and _sha512 modules, but these are provided by
_hashlib; _weakref becomes a builtin module; xxsubtype goes away (it's only for
testing/devel purposes)
- fixup patches 3, 4, 6, 8, 102, 103, 105, 111 for the rebase
- remove upstream patches: 7 (system expat), 106, 107, 108 (audioop reformat
plus CVE-2010-1634 and CVE-2010-2089), 109 (CVE-2008-5983)
- add machinery for rebuilding "configure" and friends, using the correct
version of autoconf (patch 300)
- patch the debug build's usage of COUNT_ALLOCS to be less verbose (patch 125)
- "modulator" was removed upstream
- drop "-b" from patch applications affecting .py files to avoid littering the
installation tree

* Thu Aug 19 2010 Toshio Kuratomi <toshio@fedoraproject.org> - 3.1.2-13
- Turn on computed-gotos.
- Fix for parallel make and graminit.c

* Fri Jul  2 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.2-12
- rebuild

* Fri Jul  2 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.2-11
- Fix an incompatibility between pyexpat and the system expat-2.0.1 that led to
a segfault running test_pyexpat.py (patch 110; upstream issue 9054; rhbz#610312)

* Fri Jun  4 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.2-10
- ensure that the compiler is invoked with "-fwrapv" (rhbz#594819)
- reformat whitespace in audioop.c (patch 106)
- CVE-2010-1634: fix various integer overflow checks in the audioop
module (patch 107)
- CVE-2010-2089: further checks within the audioop module (patch 108)
- CVE-2008-5983: the new PySys_SetArgvEx entry point from r81399 (patch 109)

* Thu May 27 2010 Dan Horák <dan[at]danny.cz> - 3.1.2-9
- reading the timestamp counter is available only on some arches (see Python/ceval.c)

* Wed May 26 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.2-8
- add flags for statvfs.f_flag to the constant list in posixmodule (i.e. "os")
(patch 105)

* Tue May 25 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.2-7
- add configure-time support for COUNT_ALLOCS and CALL_PROFILE debug options
(patch 104); enable them and the WITH_TSC option within the debug build

* Mon May 24 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.2-6
- build and install two different configurations of Python 3: debug and
standard, packaging the debug build in a new "python3-debug" subpackage
(patch 103)

* Tue Apr 13 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.2-5
- exclude test_http_cookies when running selftests, due to hang seen on
http://koji.fedoraproject.org/koji/taskinfo?taskID=2088463 (cancelled after
11 hours)
- update python-gdb.py from v5 to py3k version submitted upstream

* Wed Mar 31 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.2-4
- update python-gdb.py from v4 to v5 (improving performance and stability,
adding commands)

* Thu Mar 25 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.2-3
- update python-gdb.py from v3 to v4 (fixing infinite recursion on reference
cycles and tracebacks on bytes 0x80-0xff in strings, adding handlers for sets
and exceptions)

* Wed Mar 24 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.2-2
- refresh gdb hooks to v3 (reworking how they are packaged)

* Sun Mar 21 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.2-1
- update to 3.1.2: http://www.python.org/download/releases/3.1.2/
- drop upstreamed patch 2 (.pyc permissions handling)
- drop upstream patch 5 (fix for the test_tk and test_ttk_* selftests)
- drop upstreamed patch 200 (path-fixing script)

* Sat Mar 20 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-28
- fix typo in libpython.stp (rhbz:575336)

* Fri Mar 12 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-27
- add pyfuntop.stp example (source 7)
- convert usage of $$RPM_BUILD_ROOT to %%{buildroot} throughout, for
consistency with python.spec

* Mon Feb 15 2010 Thomas Spura <tomspur@fedoraproject.org> - 3.1.1-26
- rebuild for new package of redhat-rpm-config (rhbz:564527)
- use 'install -p' when running 'make install'

* Fri Feb 12 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-25
- split configure options into multiple lines for easy of editing
- add systemtap static markers (wcohen, mjw, dmalcolm; patch 8), a systemtap
tapset defining "python.function.entry" and "python.function.return" to make
the markers easy to use (dmalcolm; source 5), and an example of using the
tapset to the docs (dmalcolm; source 6) (rhbz:545179)

* Mon Feb  8 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-24
- move the -gdb.py file from %%{_libdir}/INSTSONAME-gdb.py to
%%{_prefix}/lib/debug/%%{_libdir}/INSTSONAME.debug-gdb.py to avoid noise from
ldconfig (bug 562980), and which should also ensure it becomes part of the
debuginfo subpackage, rather than the libs subpackage
- introduce %%{py_SOVERSION} and %%{py_INSTSONAME} to reflect the upstream
configure script, and to avoid fragile scripts that try to figure this out
dynamically (e.g. for the -gdb.py change)

* Mon Feb  8 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-23
- add gdb hooks for easier debugging (Source 4)

* Thu Jan 28 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-22
- update python-3.1.1-config.patch to remove downstream customization of build
of pyexpat and elementtree modules
- add patch adapted from upstream (patch 7) to add support for building against
system expat; add --with-system-expat to "configure" invocation
- remove embedded copies of expat and zlib from source tree during "prep"

* Mon Jan 25 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-21
- introduce %%{dynload_dir} macro
- explicitly list all lib-dynload files, rather than dynamically gathering the
payload into a temporary text file, so that we can be sure what we are
shipping
- introduce a macros.pybytecompile source file, to help with packaging python3
modules (Source3; written by Toshio)
- rename "2to3-3" to "python3-2to3" to better reflect python 3 module packaging
plans

* Mon Jan 25 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-20
- change python-3.1.1-config.patch to remove our downstream change to curses
configuration in Modules/Setup.dist, so that the curses modules are built using
setup.py with the downstream default (linking against libncursesw.so, rather
than libncurses.so), rather than within the Makefile; add a test to %%install
to verify the dso files that the curses module is linked against the correct
DSO (bug 539917; changes _cursesmodule.so -> _curses.so)

* Fri Jan 22 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-19
- add %%py3dir macro to macros.python3 (to be used during unified python 2/3
builds for setting up the python3 copy of the source tree)

* Wed Jan 20 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-18
- move lib2to3 from -tools subpackage to main package (bug 556667)

* Sun Jan 17 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-17
- patch Makefile.pre.in to avoid building static library (patch 6, bug 556092)

* Fri Jan 15 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-16
- use the %%{_isa} macro to ensure that the python-devel dependency on python
is for the correct multilib arch (#555943)
- delete bundled copy of libffi to make sure we use the system one

* Fri Jan 15 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-15
- fix the URLs output by pydoc so they point at python.org's 3.1 build of the
docs, rather than the 2.6 build

* Wed Jan 13 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-14
- replace references to /usr with %%{_prefix}; replace references to
/usr/include with %%{_includedir} (Toshio)

* Mon Jan 11 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-13
- fix permission on find-provides-without-python-sonames.sh from 775 to 755

* Mon Jan 11 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-12
- remove build-time requirements on tix and tk, since we already have
build-time requirements on the -devel subpackages for each of these (Thomas
Spura)
- replace usage of %%define with %%global (Thomas Spura)
- remove forcing of CC=gcc as this old workaround for bug 109268 appears to
longer be necessary
- move various test files from the "tools"/"tkinter" subpackages to the "test"
subpackage

* Thu Jan  7 2010 David Malcolm <dmalcolm@redhat.com> - 3.1.1-11
- add %%check section (thanks to Thomas Spura)
- update patch 4 to use correct shebang line
- get rid of stray patch file from buildroot

* Tue Nov 17 2009 Andrew McNabb <amcnabb@mcnabbs.org> - 3.1.1-10
- switched a few instances of "find |xargs" to "find -exec" for consistency.
- made the description of __os_install_post more accurate.

* Wed Nov  4 2009 David Malcolm <dmalcolm@redhat.com> - 3.1.1-9
- add macros.python3 to the -devel subpackage, containing common macros for use
when packaging python3 modules

* Tue Nov  3 2009 David Malcolm <dmalcolm@redhat.com> - 3.1.1-8
- add a provides of "python(abi)" (see bug 532118)
- fix issues identified by a.badger in package review (bug 526126, comment 39):
  - use "3" thoughout metadata, rather than "3.*"
  - remove conditional around "pkg-config openssl"
  - use standard cleanup of RPM_BUILD_ROOT
  - replace hardcoded references to /usr with _prefix macro
  - stop removing egg-info files
  - use /usr/bin/python3.1 rather than /use/bin/env python3.1 when fixing
up shebang lines
  - stop attempting to remove no-longer-present .cvsignore files
  - move the post/postun sections above the "files" sections

* Thu Oct 29 2009 David Malcolm <dmalcolm@redhat.com> - 3.1.1-7
- remove commented-away patch 51 (python-2.6-distutils_rpm.patch): the -O1
flag is used by default in the upstream code
- "Makefile" and the config-32/64.h file are needed by distutils/sysconfig.py
_init_posix(), so we include them in the core package, along with their parent
directories (bug 531901)

* Tue Oct 27 2009 David Malcolm <dmalcolm@redhat.com> - 3.1.1-6
- reword description, based on suggestion by amcnabb
- fix the test_email and test_imp selftests (patch 3 and patch 4 respectively)
- fix the test_tk and test_ttk_* selftests (patch 5)
- fix up the specfile's handling of shebang/perms to avoid corrupting
test_httpservers.py (sed command suggested by amcnabb)

* Thu Oct 22 2009 David Malcolm <dmalcolm@redhat.com> - 3.1.1-5
- fixup importlib/_bootstrap.py so that it correctly handles being unable to
open .pyc files for writing (patch 2, upstream issue 7187)
- actually apply the rpath patch (patch 1)

* Thu Oct 22 2009 David Malcolm <dmalcolm@redhat.com> - 3.1.1-4
- update patch0's setup of the crypt module to link it against libcrypt
- update patch0 to comment "datetimemodule" back out, so that it is built
using setup.py (see Setup, option 3), thus linking it statically against
timemodule.c and thus avoiding a run-time "undefined symbol:
_PyTime_DoubleToTimet" failure on "import datetime"

* Wed Oct 21 2009 David Malcolm <dmalcolm@redhat.com> - 3.1.1-3
- remove executable flag from various files that shouldn't have it
- fix end-of-line encodings
- fix a character encoding

* Tue Oct 20 2009 David Malcolm <dmalcolm@redhat.com> - 3.1.1-2
- disable invocation of brp-python-bytecompile in postprocessing, since
it would be with the wrong version of python (adapted from ivazquez'
python3000 specfile)
- use a custom implementation of __find_provides in order to filter out bogus
provides lines for the various .so modules
- fixup distutils/unixccompiler.py to remove standard library path from rpath
(patch 1, was Patch0 in ivazquez' python3000 specfile)
- split out libraries into a -libs subpackage
- update summaries and descriptions, basing content on ivazquez' specfile
- fixup executable permissions on .py, .xpm and .xbm files, based on work in
ivazquez's specfile
- get rid of DOS batch files
- fixup permissions for shared libraries from non-standard 555 to standard 755
- move /usr/bin/python*-config to the -devel subpackage
- mark various directories as being documentation

* Thu Sep 24 2009 Andrew McNabb <amcnabb@mcnabbs.org> 3.1.1-1
- Initial package for Python 3.

