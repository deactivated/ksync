=======================================================================
KSync - Sync the directory layout with the collections file on a Kindle
=======================================================================

The Kindle allows you to upload documents via USB by simply placing
them in the /documents directory or any of its subdirectories.
However, there is no way to navigate this hierarchy on the device
itself.  KSync is a simple python script that simulates that feature
by creating a collection for each subdirectory in /documents.

Usage
=====

Run KSync to write a new collections table to the Kindle.::

  $ ./ksync.py /Volumes/Kindle

In order to make the Kindle recognize the new collections table, you
need to unmount it and then do a hard reset by holding the power
switch for 15 seconds.
