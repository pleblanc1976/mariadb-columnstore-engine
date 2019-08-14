/* Copyright (C) 2019 MariaDB Corporation

   This program is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License
   as published by the Free Software Foundation; version 2 of
   the License.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
   MA 02110-1301, USA. */


#include <unistd.h>
#include <string>
#include <iostream>
#include <stdio.h>
#include <cstdlib>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <signal.h>

using namespace std;

#include "SMLogging.h"
#include "SessionManager.h"
#include "IOCoordinator.h"
#include "Cache.h"
#include "Synchronizer.h"
#include "Replicator.h"

using namespace storagemanager;

bool signalCaught = false;

void printCacheUsage(int sig)
{
    Cache::get()->validateCacheSize();
    cout << "Current cache size = " << Cache::get()->getCurrentCacheSize() << endl;
    cout << "Cache element count = " << Cache::get()->getCurrentCacheElementCount() << endl;
}

void printKPIs(int sig)
{
    IOCoordinator::get()->printKPIs();
    Cache::get()->printKPIs();
    Synchronizer::get()->printKPIs();
    CloudStorage::get()->printKPIs();
    Replicator::get()->printKPIs();
}

void shutdownSM(int sig)
{
    if (!signalCaught)
        (SessionManager::get())->shutdownSM(sig);
    signalCaught = true;
}

int main(int argc, char** argv)
{

    /* Instantiate objects to have them verify config settings before continuing */
    IOCoordinator* ioc = IOCoordinator::get();
    Cache* cache = Cache::get();
    Synchronizer* sync = Synchronizer::get();
    Replicator* rep = Replicator::get();

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));

    for (int i=1; i<SIGRTMAX; i++)
    {
        sa.sa_handler = shutdownSM;
        if (i != SIGCONT && i != SIGKILL && i != SIGSTOP)
            sigaction(i, &sa, NULL);
    }

    sa.sa_handler = SIG_IGN;
    sigaction(SIGPIPE, &sa, NULL);
 
    sa.sa_handler = printCacheUsage;
    sigaction(SIGUSR1, &sa, NULL);
 
    sa.sa_handler = printKPIs;
    sigaction(SIGUSR2, &sa, NULL);
    
    int ret = 0;

    SMLogging* logger = SMLogging::get();

    logger->log(LOG_NOTICE,"StorageManager started.");

    SessionManager* sm = SessionManager::get();

    ret = sm->start();

    cache->shutdown();
    
    delete sync;
    delete cache;
    delete ioc;
    delete rep;
    logger->log(LOG_INFO,"StorageManager Shutdown Complete.");

    return ret;
}

