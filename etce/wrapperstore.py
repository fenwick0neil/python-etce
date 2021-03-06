#
# Copyright (c) 2015-2017 - Adjacent Link LLC, Bridgewater, New Jersey
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

import json
import os


class WrapperStore(object):
    def __init__(self, backingfilename):
        if len(backingfilename) == 0:
            raise ValueError('ETCEStore backingfilename cannot be length 0.')

        self._backingfile = backingfilename


    def read(self):
        store = {}

        with open(self._backingfile, 'r') as fd:
            # read out
            try:
                store = json.load(fd)
            except:
                pass

        return store


    def update(self, namevaldict, section=None):
        store = {}

        if os.path.exists(self._backingfile):
            with open(self._backingfile, 'r') as fd:    
                # read out
                try:
                    store = json.load(fd)
                except:
                    pass

        if section:
            # add to subsection
            if not section in store:
                store[section] = {}
            store[section].update(namevaldict)
        else:
            # add to root
            store.update(namevaldict)

        with open(self._backingfile, 'w+') as fd:
            # write back out
            json.dump(store, fd)
