Nodeshot CitySDK Synchronizers
==============================

.. image:: https://ci.publicwifi.it/buildStatus/icon?job=nodeshot-citysdk-synchronizers

Additional nodeshot synchronizers developed for the CitySDK project.

More information on nodeshot synchronizers here: http://nodeshot.rtfd.org/en/latest/topics/synchronizers.html

Install
*******

.. code-block:: bash

    pip install nodeshot_citysdk_synchronizers

Setup
*****

Add ``nodeshot_citysdk_synchronizers`` to ``settings.INSTALLED_APPS``.

.. code-block:: python

    # settings.py
    INSTALLED_APPS.append('nodeshot_citysdk_synchronizers')

Usage
*****

Use the synchronizers as any other nodeshot synchronizer, each synchronizer
will show its configuration fields upon selection.

License (BSD)
=============

Copyright (C) 2014 Federico Capoano

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
