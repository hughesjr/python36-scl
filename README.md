# python36-scl
python36 SCL for CentOS-7.6.1810 build deps

Using the bootstrap procedures in the rh-python36-python spec file to build.

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

Note: For Step 2 , setuptools is first, then pip after setup tools .. same for Step 4.

How I normally do the bootstrap version numbers is for the bootstrap build, I add a 0. in front of the release .. as shown in this commit:

https://github.com/hughesjr/python36-scl/commit/743bcd4de8576cdd5a6713f281722f07d93d19be

Then on the subsequent (real) build, use the actual Release without the zero.

