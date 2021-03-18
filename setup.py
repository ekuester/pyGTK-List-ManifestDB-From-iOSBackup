#!/usr/bin/env python3
from setuptools import find_packages, setup

with open('VERSION') as f:
    VERSION=f.read()

setup(
    name='pyList-ManifestDB-iOSBackup',
    version=VERSION,
    description="Tool to interact with iOS backups",
    url='https://github.com/ekuester/pyGTK-List-ManifestDB-from-iOSBackup',
    author="Erich Küster",
    author_email='erich.kuester@arcor.de',
    packages=['pyList-ManifestDB-iOSBackup'],
    license="MIT",
    classifiers=[
        'Development Status :: 12 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        ],
    keywords='iOS backup Manifest.db',
    package_data={
        # include files found in the "pyXMLGPX-parser" package
        'pyList-ManifestDB-iOSBackup': ['*.xpm', 'COMMENTS', 'LICENSE', 'locale/*/LC_MESSAGES/*.mo'],
    },
    package_include=[True],
    zip_safe=False,
)
