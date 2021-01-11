<h1 align="center">
    SPACELAB PACKET DECODER
    <br>
</h1>

<h4 align="center">Packet decoder of the SpaceLab's satellites.</h4>

<p align="center">
    <a href="https://github.com/spacelab-ufsc/spacelab-decoder">
        <img src="https://img.shields.io/badge/status-development-green?style=for-the-badge">
    </a>
    <a href="https://github.com/spacelab-ufsc/spacelab-decoder/releases">
        <img src="https://img.shields.io/badge/version-0.2-blue?style=for-the-badge">
    </a>
    <a href="https://github.com/spacelab-ufsc/spacelab-decoder/blob/master/LICENSE">
        <img src="https://img.shields.io/badge/license-GPL3-yellow?style=for-the-badge">
    </a>
</p>

<p align="center">
    <a href="#overview">Overview</a> •
    <a href="#satellites">Satellites</a> •
    <a href="#dependencies">Dependencies</a> •
    <a href="#license">License</a>
</p>

## Overview

SpaceLab Packet Decoder is a software to decode audio records from the satellites of SpaceLab. For now, this software is still under development and are not functional yet.

## Satellites

* FloripaSat-I (launched in December 2019)
* GOLDS-UFSC (to be launched on 2021)

## Dependencies

* gi
* scipy
* python3-zmq
* gnuradio

## Building and Installing

Before installing the main Python application, the NGHam library must be compiled and installed in the system:

* ```make```
* ```make install```
* ```python setup.py install```

## License

This project is licensed under GPLv3 license.
