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

import os.path

import etce.utils
from etce.overlayerror import OverlayError
from etce.overlaycsvreader import OverlayCSVReader


class OverlayChainFactory(object):
    def __init__(self, mergedir):
        self._mergedir = mergedir


    def make(self, overlayelems, overlaycsvelems):
        overlaydict = {}

        for overlayelem in overlayelems:
            #<overlay tag='FREQ1' val='2347000000'/>
            tag = overlayelem.attrib['tag']

            val = overlayelem.attrib['value']

            overlaydict[tag] = etce.utils.configstrtoval(val)

        for overlaycsvelem in overlaycsvelems:
            #<overlaycsv file='FREQ1' column='2347000000'/>
            csvfile = overlaycsvelem.attrib['file']

            fullcsvfile = os.path.join(self._mergedir, csvfile)

            column = overlaycsvelem.attrib['column']

            if not os.path.isfile(fullcsvfile):
                message = 'Cannot find overlay csvfile "%s" in ' \
                          'test directory or basedirectory. Quitting' \
                          % csvfile
                raise OverlayError(message)
                
            overlays = OverlayCSVReader(fullcsvfile).values(column)
            
            overlaydict.update(overlays)

        return overlaydict