#
# Copyright (c) 2013-2017 - Adjacent Link LLC, Bridgewater, New Jersey
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

import os
import socket
import shutil
import stat
import sys
import time

from platform import Platform
from config import ConfigDictionary
from lxcplandoc import LXCPlanDoc


class LXC:
    def __init__(self):
        # check root
        if not os.geteuid() == 0:
            raise RuntimeError('You need to be root to perform this command.')
        self._platform = Platform()


    def start(self, lxcplanfile, writehosts, forcelxcroot=False):
        plandoc = LXCPlanDoc(lxcplanfile)

        hostname = socket.gethostname().split('.')[0]
        lxcrootdir = plandoc.lxcrootdirectory(hostname)
        containers = plandoc.containers(hostname)

        if not lxcrootdir[0] == '/':
            print 'rootdirectory "%s" for hostname "%s" is not an absolute path. Quitting.' % \
                (lxcrootdir, hostname)
            return

        directory_level = len(lxcrootdir.split('/')) - 1
        if not directory_level >= 3:
            print 'rootdirectory "%s" for hostname "%s" is less than 3 levels deep. Quitting.' % \
                (lxcrootdir, hostname)
            return

        allowed_roots = ('tmp', 'opt', 'home', 'var', 'mnt')
        if not lxcrootdir.split('/')[1] in allowed_roots:
            print 'rootdirectory "%s" for hostname "%s" is not located in one of {%s} ' \
                'directory trees. Quitting.' % \
                (lxcrootdir, hostname, ', '.join(allowed_roots))
            return

        if lxcrootdir is None or len(containers) == 0:
            print 'No containers assigned to host %s. Quitting.' % hostname
            return

        # delete and remake the node root
        if os.path.exists(lxcrootdir):
            if forcelxcroot:
                print 'Force removal of "%s" lxc root directory.' \
                    % lxcrootdir
                shutil.rmtree(lxcrootdir)
            else:
                print '%s lxc root directory already exists, Quitting.' \
                    % lxcrootdir
                return
                
        os.makedirs(lxcrootdir)

        # lockfile
        self._setlockfile(self._getlockfilename(), plandoc, hostname)

        # set kernelparameters
        kernelparameters = plandoc.kernelparameters(hostname)
        if len(kernelparameters) > 0:
            print 'Setting kernel parameters:'

            for kernelparamname,kernelparamval in kernelparameters.items():
                os.system('sysctl %s=%s' % (kernelparamname,kernelparamval))

        # bring up bridge
        for _,bridge in plandoc.bridges(hostname).items():
            if not bridge.persistent:
                print 'Bringing up bridge: %s' % bridge.devicename

                self._platform.bridgeup(bridge.devicename,
                                        bridge.addifs,
                                        enablemulticastsnooping=True)

                if not bridge.ipv4 is None:
                    self._platform.adddeviceaddress(bridge.devicename,
                                                    bridge.ipv4)

                if not bridge.ipv6 is None:
                    self._platform.adddeviceaddress(bridge.devicename,
                                                    bridge.ipv6)

            elif not self._platform.isdeviceup(bridge.devicename):
                raise RuntimeError('Bridge %s marked persistent is not up. Quitting.')

        if writehosts:
            self._writehosts(containers)

        # create container files
        for container in containers:
            nodedirectory = container.nodedirectory

            self._makedirs(nodedirectory)

            # make the config
            with open(os.path.join(nodedirectory, 'config'), 'w') as configf:
                configf.write(str(container))

            # make init script
            filename,initscripttext = container.initscript

            if initscripttext:
                scriptfile = os.path.join(nodedirectory, filename)

                with open(scriptfile, 'w') as sf:
                    sf.write(initscripttext)

                    os.chmod(scriptfile, 
                             stat.S_IRWXU | stat.S_IRGRP | \
                             stat.S_IXGRP | stat.S_IROTH | \
                             stat.S_IXOTH)

            
        self._startnodes(containers)


    def stop(self, forcedelete=False):
        # check for lockfile
        lockfilename = self._getlockfilename()

        if not os.path.exists(lockfilename) or not os.path.isfile(lockfilename):
            raise RuntimeError(
                'Lockfile does not exist, no shutdown')

        plandoc = LXCPlanDoc(lockfilename)
        hostname = socket.gethostname().split('.')[0]
        noderoot = plandoc.lxcrootdirectory(hostname)

        for container in plandoc.containers(hostname):
            command = 'lxc-stop -n %s -k &> /dev/null' % container.lxcname
            print command
            os.system(command)

        for _,bridge in plandoc.bridges(hostname).items():
            if not bridge.persistent:
                print 'Bringing down bridge: %s' % bridge.devicename
                self._platform.bridgedown(bridge.devicename)

        os.remove(lockfilename)


    def _makedirs(self, noderoot):
        os.makedirs(noderoot)

        vardir = os.path.join(noderoot, 'var')
        os.makedirs(vardir)
        os.makedirs(os.path.join(vardir, 'run'))
        os.makedirs(os.path.join(vardir, 'log'))
        os.makedirs(os.path.join(vardir, 'lib'))

        mntdir = os.path.join(noderoot, 'mnt')
        os.makedirs(mntdir)


    def _getlockfilename(self):
        lockfiledir = ConfigDictionary().get('etce', 'LOCK_FILE_DIRECTORY')

        if not os.path.exists(lockfiledir) or not os.path.isdir(lockfiledir):
            raise RuntimeError('Lockfile directory "%s" does not exist or is not a directory. ' \
                               'Please create it or configure LOCK_FILE_DIRECTORY in your etce.conf file.' \
                               % lockfiledir)

        return os.path.join(lockfiledir, 'etce.lxc.lock')


    def _setlockfile(self, lockfile, plandoc, hostname):
        if os.path.isfile(lockfile):
            err = 'Detected an active lxc field with root at: %s. ' \
                  'Run "etcelxc stop" first.' % plandoc.lxcrootdirectory(hostname)
            raise RuntimeError(err)
        else:
            with open(lockfile, 'w') as lf:
                lf.write(str(plandoc))


    def _startnodes(self, containers):
        for container in containers:
            noderoot = container.nodedirectory
            lxcname = container.lxcname
            command = 'lxc-execute -f %s/config  ' \
                      '-n %s '                     \
                      '-o %s/log '                 \
                      '-- %s/init.sh '             \
                      '2> /dev/null &' %             \
                      (noderoot, lxcname, noderoot, noderoot)
            
            print command
            os.system(command)


    def _waitstart(self, nodecount, lxcroot):
        numstarted = 0
        for i in range(10):
            command = 'lxc-ls -1 --active'
            numstarted = len(self._platform.runcommand(command))
            print 'Waiting for lxc containers: %d of %d are running.' % \
                (numstarted, nodecount)

            if numstarted == nodecount:
                break

            time.sleep(1)

        print 'Continuing with %d of %d running lxc containers.' % \
            (numstarted, nodecount)

        
    def _writehosts(self, containers):
        opentag = '#### Start auto-generated ETCE control mappings\n'
        closetag = '#### Stop auto-generated ETCE control mappings\n'
        etcehostlines = []
        searchstate = 0
        for line in open('/etc/hosts', 'r'):
            if searchstate == 0:
                if line.startswith(opentag):
                    searchstate = 1
                else:
                    etcehostlines.append(line)   
            elif searchstate == 1:
                if line.startswith(closetag):
                    searchstate == 2
            else:
                etcehostlines.append(line)

        # strip off trailing white spaces
        etcehostlines.reverse()
        for i,line in enumerate(etcehostlines):
            if len(line.strip()) > 0:
                etcehostlines = etcehostlines[i:]
                break
        etcehostlines.reverse()

        with open('/etc/hosts', 'w') as ofd:
            for line in etcehostlines:
                ofd.write(line)

            ofd.write('\n')
            ofd.write(opentag)
            
            # ipv4
            ipv4_entries = []
            for container in containers:
                for _,entrytpl in container.hosts_entries_ipv4.items():
                    hostentry,hostaddr = entrytpl
                    ipv4_entries.append((hostentry,hostaddr))
            for hostentry,hostaddr in sorted(ipv4_entries):
                ofd.write('%s %s\n' % (hostaddr,hostentry))

            #ipv6 = []
            ipv6_entries = []
            for container in containers:
                for _,entrytpl in container.hosts_entries_ipv6.items():
                    hostentry,hostaddr = entrytpl
                    ipv6_entries.append((hostaddr,hostentry))
            for hostentry,hostaddr in sorted(ipv6_entries):
                ofd.write('%s %s\n' % (hostaddr,hostentry))

            ofd.write(closetag)