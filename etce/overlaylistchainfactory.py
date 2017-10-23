#
# Copyright (c) 2014-2017 - Adjacent Link LLC, Bridgewater, New Jersey
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
# * Neither the name of Adjacent Link LLC nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

from etce.utils import nodestrtonodes,configstrtoval
from etce.overlayerror import OverlayError


class OverlayListChainFactory(object):
    def __init__(self):
        pass

    def make(self, overlaylistelems, indiceslist):
        valsmap = {}
        for index in indiceslist:
            valsmap[index] = {}

        for overlaylistelem in overlaylistelems:
            tag = overlaylistelem.attrib['tag']
            separator=overlaylistelem.attrib.get('separator',',')
            values = overlaylistelem.attrib['values'].split(separator)

            # number of indices and vals must agree
            if not len(indiceslist) == len(values):
                err = 'overlaylist error: number of indices (%d) and ' \
                      'number of values (%d) do not match for overlaylist ' \
                      'tag "%s"' % (len(indiceslist), len(values), tag)
                raise OverlayError(err)
                
            for index,value in zip(indiceslist,values):
                valsmap[index][tag] = configstrtoval(value.strip())

        return valsmap