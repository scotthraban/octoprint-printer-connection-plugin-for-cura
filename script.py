#Name: OctoPrint Printer Connection
#Info: Adds ability to print directly to OctoPrint from Cura
#Depend: printerconnection
#Type: printerconnection

#   Copyright 2015 Scott Hraban
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
__copyright__ = "Copyright (C) 2015 Scott Hraban - Released under terms of the Apache License, Version 2.0"

from plugins.OctoPrintPrinterConnection.OctoPrintPrinterConnectionGroup import OctoPrintPrinterConnectionGroup

def createPluginInstance():
	return OctoPrintPrinterConnectionGroup()


