# octoprint-printer-connection-plugin-for-cura
OctoPrint Printer Connection Plugin for Cura to allow direct printing from Cura to OctoPrint. In practice, this means that the Save icon will change to a WiFi looking icon, which when pressed will upload the gcode to your OctoPrint, and open a dialog, from which the Print button will actually start the print.

At this point you need to manually enter the OctoPrint Api Key in the source code when you install - sub-optimal to say the least, but I have not had the time to get up to speed on Python GUI libraries. Ideally, when a OctoPrint instance is detected, a dialog would pop up (or maybe wait until actually trying to print) requesting the Api Key, which it would then store (after validation) into the Cura preferences for use next time. If anyone out there would like to contribute and/or give pointers on how one would do this, that would be much appreciated!

Installation
============
1. Create a new directory in your Cura installation's plugin directory, the name does not matter, but recommended is "OctoPrintPrinterConnection".
2. Edit the OctoPrintPrinterConnection.py file and search for the "addHeader" method call on the http client - change the line to use your OctoPrint Api Key.
3. Enable [discovery](https://github.com/foosel/OctoPrint/wiki/Plugin:-Discovery) on OctoPrint, which currently requires running on OctoPrint's devel branch.

Dependencies
============
* OctoPrint devel branch installation
* Cura with two pull requests
  * [Adding filename to the printer connection](https://github.com/daid/Cura/pull/1163)
  * [Adding printer connection plugins](https://github.com/daid/Cura/pull/1162)

Credit
======
* Includes [ssdp library](https://gist.github.com/dankrause/6000248) writen by [Dan Krause](https://gist.github.com/dankrause), released using the [Apache 2.0 License](http://www.apache.org/licenses/LICENSE-2.0)
* Inspired by the PrinterConnection work in [Cura](https://github.com/daid/Cura) by [David Braam](https://github.com/daid)
