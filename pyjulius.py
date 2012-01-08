# -*- coding: utf-8 -*-
# Copyright 2011 Antoine Bertin <diaoulael@gmail.com>
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
from xml.etree.ElementTree import XML
import re
import socket

#: Connected client state
CONNECTED = 1

#: Disconnected client state
DISCONNECTED = 2


class Client(object):
    """Client object to connect to a julius module server

    :param string host: host of the server
    :param integer port: port of the server
    :param string encoding: encoding to use to decode socket's output

    .. attribute:: host

        Host of the server

    .. attribute:: port

        Port of the server

    .. attribute:: encoding

        Encoding to use to decode socket's output

    .. attribute:: sock

        The socket used

    .. attribute:: state

        State can be one of:

        .. data:: pyjulius.CONNECTED
        .. data:: pyjulius.DISCONNECTED

    """
    def __init__(self, host='localhost', port=10500, encoding='utf-8'):
        self.host = host
        self.port = port
        self.encoding = encoding
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.state = DISCONNECTED
    
    def connect(self):
        """Connect to the server"""
        self.sock.connect((self.host, self.port))
        self.state = CONNECTED

    def disconnect(self):
        """Disconnect from the server"""
        self.sock.shutdown()
        self.sock.close()
        self.state = DISCONNECTED

    def send(self, command):
        """Send a command to the server

        :param string command: command to send

        """
        self.sock.send(command)

    def _readline(self):
        """Read a line from the server. Data is read from the socket until a character `\n` is found

        :returns: the read line
        :rtype: unicode

        """
        line = ''
        data = self.sock.recv(1)
        while data != '\n':
            line += unicode(data, self.encoding)
            data = self.sock.recv(1)
        return line

    def _readblock(self):
        """Read a block from the server. Lines are read until a character `.` is found

        :returns: the read block
        :rtype: unicode

        """
        block = ''
        line = self._readline()
        while line != '.':
            block += line
            line = self._readline()
        return block

    def _readxml(self):
        """Read a block and returns the result as XML

        :returns: block as xml
        :rtype: xml.etree.ElementTree

        """
        block = re.sub(r'<(/?)s>', r'&lt;\1s&gt;', self._readblock())
        return XML(block)

    def empty(self):
        """Empty the socket"""
        self.sock.setblocking(False)
        while 1:
            try:
                self.sock.recv(4096)
            except socket.error:
                break
        self.sock.setblocking(True)

    def etree(self, tag):
        """Read the socket until the xml tag is found

        :param string tag: xml tag to wait for
        :returns: the xml element with matching tag
        :rtype: xml.etree.ElementTree

        """
        xml = self._readxml()
        while xml.tag != tag:
            xml = self._readxml()
        return xml

    def recognize(self):
        """Extract the next recognized sentence from the server

        :returns: the recognized sentence
        :rtype: :class:`Sentence`

        """
        xml = self.etree('RECOGOUT')
        shypo = xml.find('SHYPO')
        return Sentence.from_shypo(shypo, self.encoding)


class Sentence(object):
    """Sentence object that represents a recognized sentence

    :param words: words in the sentence
    :type words: list of :class:`Word`
    :param integer score: score of the sentence

    .. attribute:: words

        Words that constitute the sentence

    .. attribute:: score

        Score of the sentence

    """
    def __init__(self, words, score=0):
        self.words = words
        self.score = score

    @classmethod
    def from_shypo(cls, xml, encoding='utf-8'):
        """Constructor from xml element `SHYPO`

        :param xml.etree.ElementTree xml: the xml `SHYPO` element
        :param string encoding: encoding of the xml

        """
        score = float(xml.get('SCORE'))
        words = [Word.from_whypo(w_xml, encoding) for w_xml in xml.findall('WHYPO') if w_xml.get('WORD') not in ['<s>', '</s>']]
        return cls(words, score)

    def __repr__(self):
        return "<Sentence('%f', '%r')>" % (self.score, self.words)

    def __unicode__(self):
        return u' '.join([unicode(w) for w in self.words])


class Word(object):
    """Word object that represents a word within a sentence

    :param string word: the word
    :param float confidence: confidence of the recognized word

    .. attribute:: word

        Recognized word

    .. attribute:: confidence

        Confidence of the recognized word

    """
    def __init__(self, word, confidence=0.0):
        self.word = word
        self.confidence = confidence

    @classmethod
    def from_whypo(cls, xml, encoding='utf-8'):
        """Constructor from xml element `WHYPO`

        :param xml.etree.ElementTree xml: the xml `WHYPO` element
        :param string encoding: encoding of the xml

        """
        word = unicode(xml.get('WORD'), encoding)
        confidence = float(xml.get('CM'))
        return cls(word, confidence)

    def __repr__(self):
        return "<Word('%f','%s')>" % (self.confidence, self.word)

    def __unicode__(self):
        return self.word.lower()
