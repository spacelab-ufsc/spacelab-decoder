*********************
Packaging the Project
*********************

This page presents the instructions to packaging the source files of the project.

Generating a RPM package
========================

To generate an RPM package, follow the instructions below:

1. Run the commands below in the root directory of the project:

::

    python setup.py bdist_rpm --spec-only
    python setup.py sdist

2. Add the following line at the beginning of the generated *.spec* file (located in the *dist* folder):

::

    %define name spacelab_decoder
    %define version 0.3.0
    %define unmangled_version 0.3.0
    %define unmangled_version 0.3.0
    %define release 1

    %global debug_package %{nil}
    ...

3. Copy the output file of the *sdist* command to the *SOURCES* folder of the rpmbuild tool:

::

    cp dist/*.tar.gz ~/rpmbuild/SOURCES/

4. Execute the following command in the folder containing the *.spec* file:

::

    rpmbuild -bb spacelab_decoder.spec

5. The generated RPM package will be available in *~/rpmbuild/RPMS/x86_64/*.
