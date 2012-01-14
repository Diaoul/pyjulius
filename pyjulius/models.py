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
__all__ = ['Sentence', 'Word']


class Sentence(object):
    """A recognized sentence

    :param words: words in the sentence
    :type words: list of :class:`~pyjulius.core.Word`
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
        """Constructor from xml element *SHYPO*

        :param xml.etree.ElementTree xml: the xml *SHYPO* element
        :param string encoding: encoding of the xml

        """
        score = float(xml.get('SCORE'))
        words = [Word.from_whypo(w_xml, encoding) for w_xml in xml.findall('WHYPO') if w_xml.get('WORD') not in ['<s>', '</s>']]
        return cls(words, score)

    def __repr__(self):
        return "<Sentence(%.2f, %r)>" % (self.score, self.words)

    def __unicode__(self):
        return u' '.join([unicode(w) for w in self.words])

    def __str__(self):
        return str(self.__unicode__())

    def __len__(self):
        return len(self.words)


class Word(object):
    """A word within a :class:`~pyjulius.core.Sentence`

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
        """Constructor from xml element *WHYPO*

        :param xml.etree.ElementTree xml: the xml *WHYPO* element
        :param string encoding: encoding of the xml

        """
        word = unicode(xml.get('WORD'), encoding)
        confidence = float(xml.get('CM'))
        return cls(word, confidence)

    def __repr__(self):
        return "<Word(%.2f, %s)>" % (self.confidence, self.word)

    def __unicode__(self):
        return self.word.lower()

    def __len__(self):
        return len(self.word)
