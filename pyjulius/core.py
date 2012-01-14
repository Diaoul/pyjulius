# -*- coding: utf-8 -*-
# Copyright 2011-2012 Antoine Bertin <diaoulael@gmail.com>
#
# This file is part of pyjulius.
#
# pyjulius is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyjulius is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyjulius.  If not, see <http://www.gnu.org/licenses/>.
from exceptions import ConnectionError
from models import Sentence
from pyjulius.exceptions import SendTimeoutError
from xml.etree.ElementTree import XML, ParseError
import Queue
import logging
import re
import select
import socket
import threading


__all__ = ['CONNECTED', 'DISCONNECTED', 'Client']
logger = logging.getLogger(__name__)


#: Connected client state
CONNECTED = 1

#: Disconnected client state
DISCONNECTED = 2


class Client(threading.Thread):
    """Threaded Client to connect to a julius module server

    :param string host: host of the server
    :param integer port: port of the server
    :param string encoding: encoding to use to decode socket's output
    :param boolean modelize: try to interpret raw xml :class:`~xml.etree.ElementTree.Element` as :mod:`~pyjulius.models` if ``True``

    .. attribute:: host

        Host of the server

    .. attribute:: port

        Port of the server

    .. attribute:: encoding

        Encoding to use to decode socket's output

    .. attribute:: modelize

        Try to interpret raw xml :class:`~xml.etree.ElementTree.Element` as :mod:`~pyjulius.models` if ``True``

    .. attribute:: results

        Results received when listening to the server. This :class:`~Queue.Queue` is filled with
        raw xml :class:`~xml.etree.ElementTree.Element` objects and :class:`~pyjulius.models` (if :attr:`modelize`)

    .. attribute:: sock

        The socket used

    .. attribute:: state

        Current state. State can be:

        * :data:`~pyjulius.core.CONNECTED`
        * :data:`~pyjulius.core.DISCONNECTED`

    """
    def __init__(self, host='localhost', port=10500, encoding='utf-8', modelize=True):
        super(Client, self).__init__()
        self.host = host
        self.port = port
        self.encoding = encoding
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.state = DISCONNECTED
        self._stop = False
        self.results = Queue.Queue()
        self.modelize = modelize

    def stop(self):
        """Stop the thread"""
        self._stop = True

    def run(self):
        """Start listening to the server"""
        logger.info(u'Started listening')
        while not self._stop:
            xml = self._readxml()

            # Exit on invalid XML
            if xml is None:
                break

            # Raw xml only
            if not self.modelize:
                logger.info(u'Raw xml: %s' % xml)
                self.results.put(xml)
                continue

            # Model objects + raw xml as fallback
            if xml.tag == 'RECOGOUT':
                sentence = Sentence.from_shypo(xml.find('SHYPO'), self.encoding)
                logger.info(u'Modelized recognition: %r' % sentence)
                self.results.put(sentence)
            else:
                logger.info(u'Unmodelized xml: %s' % xml)
                self.results.put(xml)

        logger.info(u'Stopped listening')

    def connect(self):
        """Connect to the server

        :raise ConnectionError: If socket cannot establish a connection

        """
        try:
            logger.info(u'Connecting %s:%d' % (self.host, self.port))
            self.sock.connect((self.host, self.port))
        except socket.error:
            raise ConnectionError()
        self.state = CONNECTED

    def disconnect(self):
        """Disconnect from the server"""
        logger.info(u'Disconnecting')
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.state = DISCONNECTED

    def send(self, command, timeout=5):
        """Send a command to the server

        :param string command: command to send

        """
        logger.info(u'Sending %s' % command)
        _, writable, __ = select.select([], [self.sock], [], timeout)
        if not writable:
            raise SendTimeoutError()
        writable[0].send(command)

    def _readline(self):
        """Read a line from the server. Data is read from the socket until a character ``\n`` is found

        :return: the read line
        :rtype: string

        """
        line = ''
        while not self._stop:
            readable, _, __ = select.select([self.sock], [], [], 0.5)
            if not readable:
                continue
            data = readable[0].recv(1)
            if data == '\n':
                break
            line += unicode(data, self.encoding)
        return line

    def _readblock(self):
        """Read a block from the server. Lines are read until a character ``.`` is found

        :return: the read block
        :rtype: string

        """
        block = ''
        while not self._stop:
            line = self._readline()
            if line == '.':
                break
            block += line
        return block

    def _readxml(self):
        """Read a block and return the result as XML

        :return: block as xml
        :rtype: xml.etree.ElementTree

        """
        block = re.sub(r'<(/?)s>', r'&lt;\1s&gt;', self._readblock())
        try:
            xml = XML(block)
        except ParseError:
            xml = None
        return xml
