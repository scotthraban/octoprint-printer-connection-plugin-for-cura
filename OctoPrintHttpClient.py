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

import time
import urllib
import httplib as httpclient
import json
import xml.etree.ElementTree as ET
import cStringIO as StringIO
import traceback

class OctoPrintHttpClientResponse(object):
	def __init__(self, statusCode, statusMessage, body):
		self.statusCode = statusCode
		self.statusMessage = statusMessage
		self.body = body
		
	def isOk(self):
		return self.statusCode >= 200 and self.statusCode < 300
		
	def isUnauthorized(self):
		return self.statusCode == 401
		
class OctoPrintHttpClient(object):

	def __init__(self, scheme, host, port, rootPath, contentType):
		super(OctoPrintHttpClient, self).__init__()

		if scheme != "http" and scheme != "https":
			raise IllegalArgument("scheme", "scheme must be http or https")
		if host is None or host == "":
			raise IllegalArgument("host", "host must not be empty")
		if host is None or host == "":
			raise IllegalArgument("port", "port must not be empty")
		if contentType != "json" and contentType != "xml":
			raise IllegalArgument("contentType", "contentType must be json or xml")

		self._scheme = scheme
		self._host = host
		self._port = port
		self._rootPath = rootPath or ""
		self._contentType = contentType
		self._headers = {}
		
		while self._rootPath and self._rootPath[-1] == '/':
			self._rootPath = self._rootPath[:-1]

		
	def addHeader(self, key, value):
		self._headers[key] = value
		
	def request(self, method, path, postData = None, filename = None):
		if self._scheme == "https":
			http = httpclient.HTTPSConnection(self._host, self._port or 443, timeout=5)
		else:
			http = httpclient.HTTPConnection(self._host, self._port or 80, timeout=5)

		fullPath = "{}{}".format(self._rootPath, path)
			
		try:
			headers = {"User-Agent": "Cura OctoPrint Printer Connection"}
			
			for key in self._headers.keys():
				headers[key] = self._headers[key]

			if filename is not None and postData is not None:
				boundary = "OctoPrintConnectBoundary"
				
				headers["Content-type"] = "multipart/form-data; boundary={}".format(boundary)

				prefix = StringIO.StringIO()
				prefix.write('--{}\r\nContent-Disposition: form-data; name="file"; filename="{}"\r\nContent-Type: application/octet-stream\r\n\r\n'.format(boundary, filename))
				postData._list.insert(0, prefix)
				
				suffix = StringIO.StringIO()
				suffix.write("\r\n--{}--".format(boundary))
				postData._list.append(suffix)
				
				postData.seekStart()
				http.request(method, fullPath, postData, headers = headers)
			elif postData is not None:
				if self._contentType == "json":
					headers["Content-type"] = "application/json"
					http.request(method, fullPath, json.dumps(postData), headers = headers)
				else:
					headers["Content-type"] = "application/xml"
					http.request(method, fullPath, ET.tostring(postData), headers = headers)
			else:
				http.request(method, fullPath, headers = headers)
		except:
			print "Request Error: ({}:{})".format(method, fullPath)
			traceback.print_exc()
			http.close()
			return OctoPrintHttpClientResponse(0, "error making request", None)

		try:
			response = http.getresponse()
			responseText = response.read()
		except:
			print "Response Error: ({}:{})".format(method, fullPath)
			traceback.print_exc()
			http.close()
			return OctoPrintHttpClientResponse(0, "error getting response", None)

		http.close()

		if str(response.status)[0] != '2':
			print "Responded with error: ({}:{}) ({}) {}".format(method, fullPath, response.status, response.reason)
			return OctoPrintHttpClientResponse(response.status, response.reason, None)

		if responseText:
			try:
				if self._contentType == "json":
					return OctoPrintHttpClientResponse(response.status, response.reason, json.loads(responseText))
				else:
					return OctoPrintHttpClientResponse(response.status, response.reason, ET.fromstring(responseText))
			except ValueError:
				print "Error: ({}) ({}:{})".format(self._contentType, method, fullPath)
				traceback.print_exc()
				return OctoPrintHttpClientResponse(0, "Error parsing response body", None)


class Error(Exception):
	"""Base class for exceptions in this module."""
	pass
	
class IllegalArgument(Error):
	"""Exception raised for errors in the arguments.

	Attributes:
		expr -- input expression in which the error occurred
		msg  -- explanation of the error
	"""

	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
