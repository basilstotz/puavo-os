Puavo OS
========

Puavo OS is a operating system targeting servers, laptops, workstations and
digital signages. The most distinctive feature of Puavo OS is its distribution
and update mechanism; Puavo OS releases are delivered as *immutable* file system
images, rather than separate software packages. This allows Puavo OS devices to
be updated *atomically* and makes system rollbacks ridiculously easy. In fact,
there are no updates nor rollbacks per se; changing the system version is just a
matter of booting the system with a different file system image.

Puavo OS is free, it is based on Debian

Getting the source code
-----------------------

.. code-block:: shell

    git clone git@github.com:puavo-org/puavo-os.git
    cd puavo-os

Building a root file system
---------------------------

.. code-block:: shell

    sudo make rootfs ROOTFSDIR=/var/tmp/puavo-os/rootfs

Creating a root file system image
---------------------------------

.. code-block:: shell

    sudo make image ROOTFSDIR=/var/tmp/puavo-os/rootfs
