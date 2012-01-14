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
__all__ = ['Error', 'ConnectionError', 'SendTimeoutError']


class Error(Exception):
    """Base class for pyjulius exceptions"""


class ConnectionError(Error):
    """Raised when the initial connection to the server could not be established"""


class SendTimeoutError(Error):
    """Raised when could not send the command (timeout)"""
