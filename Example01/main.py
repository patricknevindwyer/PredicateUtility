#
#  main.py
#  Example01
#
#  Created by Patrick Dwyer on 1/19/11.
#  Copyright Dwyer Devices, Inc 2011. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit

from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
import Example01AppDelegate

# pass control to AppKit
AppHelper.runEventLoop()
