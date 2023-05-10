#!/usr/bin/env python
# coding: utf-8
from setuptools import setup
from setuptools import find_packages


def get_packages():
    """ List of (sub)packages to install. """
    return find_packages('src', include=('passlib_cli', 'passlib_cli.*'))


def get_requirements(filename):
    """ Read requirements from file. """
    with open(filename, 'r') as reqfile:
        for req_line in reqfile.readlines():
            req_line = req_line.strip()
            if req_line:
                yield req_line


def get_textfile(filename):
    """ Get contents from a text file. """
    with open(filename, 'r') as fh:
        return fh.read()


def run_setup():
    """ build and run setup. """

    setup(
        name='passlib-cli',
        description='CLI utils for passlib',
        long_description=get_textfile('README.md'),
        author='fredrikhl',
        license='MIT',
        url='https://github.com/fredrikhl/passlib-cli',
        use_scm_version=True,
        setup_requires=['setuptools_scm'],
        install_requires=list(get_requirements('requirements.txt')),
        packages=get_packages(),
        package_dir={'': 'src'},
        entry_points={
            'console_scripts': [
                'passlib-mkpasswd = passlib_cli.__main__:main',
            ]
        },
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Topic :: Security',
            'Topic :: System :: Systems Administration',
            'Topic :: Utilities',
        ],
    )


if __name__ == "__main__":
    run_setup()
