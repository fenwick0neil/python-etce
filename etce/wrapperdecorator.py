#
# Copyright (c) 2018 - Adjacent Link LLC, Bridgewater, New Jersey
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

import signal

class WrapperDecorator(object):
    def __init__(self, decorator_command, impl):
        self._decorator_command = decorator_command
        self._impl = impl


    def register_argument(self, argname, defaultval, description):
        self._impl.register_argument(argname, defaultval, description)


    def register_infile_name(self, name):
        self._impl.register_infile_name(name)


    def register_outfile_name(self, name):
        self._impl.register_outfile_name(name)


    def store(self, namevaldict):
        self._impl.store(namevaldict)


    @property
    def platform(self):
        return self._impl.platform


    def daemonize(self,
                  commandstr,
                  stdout=None,
                  stderr=None,
                  pidfilename=None,
                  genpidfile=True,
                  pidincrement=0,
                  starttime=None):

        self._impl.daemonize(' '.join([self._decorator_command, commandstr]),
                             stdout,
                             stderr,
                             pidfilename,
                             genpidfile,
                             pidincrement,
                             starttime)


    def run(self,
            commandstr,
            stdout=None,
            stderr=None,
            pidfilename=None,
            genpidfile=True,
            pidincrement=0):

        self._impl.run(' '.join([self._decorator_command, commandstr]),
                       stdout,
                       stderr,
                       pidfilename,
                       genpidfile,
                       pidincrement)

        
    @property
    def args(self):
        return self._impl.args


    def stop(self, pidfilename=None, signal=signal.SIGQUIT):
        self._impl.stop(pidfilename, signal, decorator=self._decorator_command)
