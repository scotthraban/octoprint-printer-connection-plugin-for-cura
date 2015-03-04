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

import os
import json
import uuid

from Cura.util.profile import getBasePath

class OctoPrintPrinter(object):

	def __init__(self, name, scheme, host, port, path, apiKey = None, key = None):
		super(OctoPrintPrinter, self).__init__()
		
		self._config = {"key": key or uuid.uuid4(),
						"name": name or "OctoPrint Printer",
						"scheme": scheme or "http",
						"host": host or "localhost",
						"port": port or 5000,
						"path": path or "",
						"apiKey": apiKey or "" }
	
	def getKey(self):
		return self._config.get("key")
		
	def setKey(self, value):
		self._config["key"] = value
		
	def getName(self):
		return self._config.get("name")
		
	def setName(self, value):
		self._config["name"] = value
		
	def getScheme(self):
		return self._config.get("scheme")
		
	def setScheme(self, value):
		self._config["scheme"] = value
		
	def getHost(self):
		return self._config.get("host")
		
	def setHost(self, value):
		self._config["host"] = value
		
	def getPort(self):
		return self._config.get("port")
		
	def setPort(self, value):
		self._config["port"] = value
		
	def getPath(self):
		return self._config.get("path")
		
	def setPath(self, value):
		self._config["path"] = value
		
	def getApiKey(self):
		return self._config.get("apiKey")
		
	def setApiKey(self, value):
		self._config["apiKey"] = value
		
	def getConfig(self):
		return self._config

		
class OctoPrintConfiguration(object):

	def __init__(self):
		super(OctoPrintConfiguration, self).__init__()

		self._config = None
		self._configFileDate = None
		
		if not os.path.exists(self._getConfigFilePath()):
			self._createDefaultConfig()
			self._writeConfigToFile()
		else:
			self._readConfigFromFile()
			
	def getDiscovery(self):
		return self._config.get("discovery")
		
	def setDiscover(self, discovery):
		self._config["discovery"] = discovery
		
	def getPrinters(self):
		printers = []
		for key in (self._config.get("printers") or {}).keys():
			if not key == "auto-generated-uuid":
				config = self._config.get("printers").get(key)
				printers.append(OctoPrintPrinter(config["name"], config["scheme"], config["host"], config["port"], config["path"], config["apiKey"], config["key"]))
		return printers
		
	def updatePrinter(self, printer):
		key = printer.getKey() or uuid.uuid4()
		printer.setKey(key)
		printers = self._config.get("printers")
		if printers is None:
			printers = {}
			self._config["printers"] = printers
		printers[key] = printer.getConfig()
		
		self._writeConfigToFile()

	def updateConfigFromFile(self):
		actualConfigFileDate = os.path.getmtime(self._getConfigFilePath())
		if actualConfigFileDate > self._configFileDate:
			self._readConfigFromFile()
			return True
		else:
			return False
	
	def _readConfigFromFile(self):
		self._config = json.loads(open(self._getConfigFilePath()).read())

		self._updateConfigFileDate()
			
	def _writeConfigToFile(self):
		config = open(self._getConfigFilePath(), "w")
		config.write(json.dumps(self._config, indent=4))
		config.close()
		
		self._updateConfigFileDate()
		
	def _updateConfigFileDate(self):
		self._configFileDate = os.path.getmtime(self._getConfigFilePath())
	
	def _createDefaultConfig(self):
		self._config = {}
		
		self._config["printers"] = []
		
		self._config["printers"] = {}
		self._config["printers"]["auto-generated-uuid"] = { "key" : "auto-generated-uuid",
															"scheme": "https",
															"host": "127.0.0.1",
															"port": 5000,
															"path": "",
															"name": "OctoPrint Example",
															"apiKey": "the-api-key"}

		self._config["discovery"] = True

	def _getConfigFilePath(self):
		return os.path.join(getBasePath(), 'octoprint_configuration.json')

