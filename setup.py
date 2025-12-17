#!/usr/bin/env python

#
#  setup.py
#  
#  Copyright The SpaceLab-Decoder Contributors.
#  
#  This file is part of SpaceLab-Decoder.
#
#  SpaceLab-Decoder is free software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  SpaceLab-Decoder is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public
#  License along with SpaceLab-Decoder; if not, see <http://www.gnu.org/licenses/>.
#  
#

import setuptools
import os

# Make sure we are running on posix (Linux, Unix, MAC OSX)
if os.name != 'posix':
    sys.exit("Sorry, Windows is not supported yet!")

exec(open('spacelab_decoder/version.py').read())

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name                            = "spacelab_decoder",
    version                         = __version__,
    author                          = "Gabriel Mariano Marcelino",
    author_email                    = "gabriel.mm8@gmail.com",
    maintainer                      = "Gabriel Mariano Marcelino",
    maintainer_email                = "gabriel.mm8@gmail.com",
    url                             = "https://github.com/spacelab-ufsc/spacelab-decoder",
    license                         = "GPLv3",
    description                     = "SpaceLab packet decoder",
    long_description                = long_description,
    long_description_content_type   = "text/markdown",
    platforms                       = ["Linux"],
    classifiers                     = [
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research"
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Communications :: Ham Radio",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        ],
    download_url                    = "https://github.com/spacelab-ufsc/spacelab-decoder/releases",
    packages                        = setuptools.find_packages(),
    install_requires                = ['PyGObject','numpy','scipy','matplotlib','pyngham','pyzmq'],
    entry_points                    = {
        'gui_scripts': [
            'spacelab-decoder = spacelab_decoder.__main__:main'
            ]
        },
    data_files                      = [
        ('share/icons/', ['spacelab_decoder/data/img/spacelab_decoder_256x256.png']),
        ('share/applications/', ['spacelab_decoder.desktop']),
        ('share/spacelab_decoder/', ['spacelab_decoder/data/ui/spacelab_decoder.glade']),
        ('share/spacelab_decoder/', ['spacelab_decoder/data/img/spacelab-logo-full-400x200.png']),
        ('share/spacelab_decoder/', ['spacelab_decoder/data/satellites/floripasat-1.json']),
        ('share/spacelab_decoder/', ['spacelab_decoder/data/satellites/floripasat-2a.json']),
        ('share/spacelab_decoder/', ['spacelab_decoder/data/satellites/golds-ufsc.json']),
        ('share/spacelab_decoder/', ['spacelab_decoder/data/satellites/spacelab-transmitter.json']),
        ('share/spacelab_decoder/', ['spacelab_decoder/data/satellites/catarina-a1.json']),
        ('share/spacelab_decoder/', ['spacelab_decoder/data/satellites/catarina-a2.json']),
        ('share/spacelab_decoder/', ['spacelab_decoder/data/satellites/catarina-a3.json']),
        ],
)
