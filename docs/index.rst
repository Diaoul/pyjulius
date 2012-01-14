.. pyjulius documentation master file, created by
   sphinx-quickstart on Sun Jan  8 12:26:02 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============
Release v\ |version|

pyjulius provides a simple interface to connect to julius module server


Example
=======
First you will need to run julius with the *-module* option (documentation `here <http://julius.sourceforge.jp/juliusbook/ja/desc_module.html>`_
or man :manpage:`julius`).
Julius will wait for a client to connect, this is what :class:`~pyjulius.core.Client` does in a threaded way.

Let's just write a simple program that will print whatever the julius server sends until you press CTRL+C::

    #!/usr/bin/env python
    import sys
    import pyjulius
    import Queue
    
    # Initialize and try to connect
    client = pyjulius.Client('localhost', 10500)
    try:
        client.connect()
    except pyjulius.ConnectionError:
        print 'Start julius as module first!'
        sys.exit(1)
    
    # Start listening to the server
    client.start()
    try:
        while 1:
            try:
                result = client.results.get(False)
            except Queue.Empty:
                continue
            print repr(result)
    except KeyboardInterrupt:
        print 'Exiting...'
        client.stop()  # send the stop signal
        client.join()  # wait for the thread to die
        client.disconnect()  # disconnect from julius

If you are only interested in recognitions, wait for an instance of :class:`~pyjulius.models.Sentence` objects in the queue::

    if isinstance(result, pyjulius.Sentence):
        print 'Sentence "%s" recognized with score %.2f' % (result, result.score)

If you do not want :class:`~pyjulius.core.Client` to interpret the raw xml :class:`~xml.etree.ElementTree.Element`,
you can set :attr:`~pyjulius.core.Client.modelize` attribute to ``False``

If you encounter any encoding issues, have a look at the *-charconv* option of julius and set the :attr:`Client.encoding <pyjulius.core.Client.encoding>`
to the right value


API Documentation
=================
More details about the use of the module can be found here

States
------
.. autodata:: pyjulius.core.CONNECTED
.. autodata:: pyjulius.core.DISCONNECTED

Client
------
.. autoclass:: pyjulius.core.Client
    :members:

Models
------
Models are designed in order to represent the server response an object-oriented and easy way

.. automodule:: pyjulius.models
    :members:

Exceptions
----------
.. automodule:: pyjulius.exceptions
    :members:
