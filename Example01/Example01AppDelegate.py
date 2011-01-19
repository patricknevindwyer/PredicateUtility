#
#  Example01AppDelegate.py
#  Example01
#
#  Created by Patrick Dwyer on 1/19/11.
#  Copyright Dwyer Devices, Inc 2011. All rights reserved.
#

from Foundation import *
from AppKit import *

class Example01AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")
