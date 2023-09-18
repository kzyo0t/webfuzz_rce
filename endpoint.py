from utils import HTTPRequest, BodyParser
import urllib
import json

# init
body_parser = BodyParser()

def merge_dict(dict1, dict2={}):
	fdict = {}
	try:
		tmp1 = list(dict1.keys())
	except:
		tmp1 = []
	try:
		tmp2 = list(dict2.keys())
	except:
		tmp2 = []

	for key in tmp1 + tmp2:
		fdict[key] = []
		data1 = []
		if key in dict1:
			if isinstance(dict1[key], list):
				data1 = dict1[key]
			else:
				data1.append(dict1[key]) 

		data2 = []
		if key in dict2:
			if isinstance(dict2[key], list):
				data2 = dict2[key]
			else:
				data2.append(dict2[key])

		fdict[key] = data1 + data2
	return fdict

def url_decode(data):
	if data:
		if isinstance(data, bytes):
			data = data.decode('utf-8')
		while data != urllib.parse.unquote(data):
			data = urllib.parse.unquote(data)
	return data

def url_pair_value_parser(raw_params):
	data = {}
	pair_data = list(filter(None, raw_params.split('&')))
	for item in pair_data:
		try:
			key, value = item.split('=')
			if Param('URL', key) in data:
				print('Something wrong? Same URL param detected.')
			else:
				data[Param('URL', key)] = [value]
		except:
			pass
	return data

def URL_parser(url):
	locate = url.find('?')
	if locate >= 0:
		uri, params = url[:locate], url[locate+1:]
		params = url_pair_value_parser(params)
	else:
		params = {}
		uri = url
	# string, dict
	return uri, params

class Param(object):
	def __init__(self, type, name):
		self.type = type
		self.name = name
	
	def __lt__(self, other):
		if isinstance(other, Param):
			if hash(self) < hash(other):
				return True
		return False

	def __eq__(self, other):
		if isinstance(other, Param):
			if hash(self) == hash(other):
				return True
		return False

	def __hash__(self):
		return hash((self.type, self.name))
	
	def __repr__(self):
		return str(self.__dict__)


class Endpoint(object):
	def __init__(self, url, method, path, raw_request=None, params=None):
		self.url = url
		self.methods = [method]
		self.path = path
		self.params = {}

		if raw_request != None:
			raw_headers, raw_body = raw_request.split(b'\r\n\r\n', 1)

			# parse headers
			tmp = HTTPRequest(raw_headers)
			requestline = tmp.raw_requestline
			self.headers = dict(tmp.headers)

			# parse requests line
			self.path, self.params = URL_parser(url_decode(self.path))

			# parse body
			try:
				new_params, detect_content_type = body_parser.parse( \
														raw_body, \
														self.headers['Content-Type'] \
													)
				if type(new_params) is dict:
					for key, value in new_params.items():
						if 'json' in detect_content_type:
							self.params[Param('Body JSON', key)] = [value]
						elif 'multipart' in detect_content_type:
							if isinstance(value, list):
								self.params[Param('Body Multipart', key)] = value
							else:
								self.params[Param('Body Multipart', key)] = [value]
						else:
							self.params[Param('Body', key)] = [value]
			except KeyError:
				# request have no body
				pass
		if params:
			self.params = params

		if self.params:
			self.sample_requests_count = 1
		else:
			self.sample_requests_count = 0


	def __eq__(self, other):
		if isinstance(other, Endpoint):
			if hash(self) == hash(other):
				return True
		return False
	
	def __hash__(self):
		return hash((self.url, self.path, str(sorted(self.params.keys()))))
		# return hash(self.path)

	def __add__(self, other):
		if isinstance(other, Endpoint):
			if self.params == other.params:
				return self

			for param in self.params:
				if param not in other.params:
					self.params[param].append(None)
			for param in other.params:
				if param not in self.params:
					other.params[param] = [None]*self.sample_requests_count + other.params[param]
			self.params = merge_dict(self.params, other.params)
			self.methods = list(set(self.methods + other.methods))
			self.sample_requests_count += 1
			return self
		else:
			raise ValueError('Endpoint can\'t add() %s type' % type(other))

class Header(Endpoint):
	@staticmethod
	def convert_headers_params(headers):
		params = {}
		for param, value in headers.items():
			params[Param('Header', param)] = [value]
		
		return params
	
	def __hash__(self):
		return hash((self.url, self.path))
