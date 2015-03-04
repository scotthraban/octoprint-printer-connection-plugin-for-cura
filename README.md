# octoprint-printer-connection-plugin-for-cura
OctoPrint Printer Connection Plugin for Cura to allow direct printing from Cura to OctoPrint. In practice, this means that the Save icon will change to a WiFi looking icon, which when pressed will upload the gcode to your OctoPrint, and open a dialog, from which the Print button will actually start the print.

This plugin stored its configuration in a file called octoprint_configuration.json in the same folder that Cura keeps its preferences. This file can be modified to manually add printers, turn auto discovery on/off, or to enter an API Key for an auto discovered printer.

I have not had the time to get up to speed on Python GUI libraries, but ideally, when a OctoPrint instance is detected, a dialog would pop up (or maybe wait until actually trying to print) requesting the API Key, which it would then store (after validation) into the configuration file for use next time. If anyone out there would like to contribute and/or give pointers on how one would do this, that would be much appreciated!

Installation
============
1. Create a new directory in your Cura installation's plugin directory, the name does not matter, but recommended is "OctoPrintPrinterConnection".
2. Start Cura
3. (optional) Enable [discovery](https://github.com/foosel/OctoPrint/wiki/Plugin:-Discovery) on OctoPrint, which currently requires running on OctoPrint's devel branch. Edit the octoprint_configuration to add the API Key to the entry created by auto discovery.
4. (optional) Edit the octoprint_configuration.json file to manually add a printer that cannot be found using auto discovery.
5. Wait a little while for the octoprint configuration file to be reloaded.

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
