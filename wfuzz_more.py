# coding: utf-8
import xml.dom.minidom
from xml.parsers.expat import ExpatError
from codecs import decode, encode
import urllib.parse
import json
import string
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font, colors, NamedStyle
from openpyxl.comments import Comment
from utils import BodyParser, HTTPRequest
from endpoint import Endpoint, Header
import base64
import pprint
from webFuzz.node_iterator import NodeIterator
from webFuzz.environment   import env
from webFuzz.types  import Arguments,InstrumentArgs
import json
from webFuzz.node import Node
import os
import wfuzz

pp = pprint.PrettyPrinter(indent=4)
parser = BodyParser()

###code header############
def fold(header):
  line = "%s: %s" % (header[0], header[1])
  if len(line) < 998: 
    return line
  else: #fold
    lines = [line]
    while len(lines[-1]) > 998:
      split_this = lines[-1]
      #find last space in longest chunk admissible
      split_here = split_this[:998].rfind(" ")
      del lines[-1]
      lines = lines + [split_this[:split_here],split_this[split_here:]] #this may still be too long
                                                 #hence the while on lines[-1]
    return "\n".join(lines)

def dict2header(data):
  return "\n".join((fold(header) for header in data.items()))

def header2dict(data):
  data = data.replace("\n ", " ").splitlines()
  headers = {}
  for line in data:
    split_here = line.find(":")
    headers[line[:split_here]] = line[split_here+2:]
  return headers
###code header############


def condition_checker(node):
    try:
        status = node.getElementsByTagName("status")[0].firstChild.data
        if status in ['400','404','405','501','500','301']:
            return False
    except:
        # Null => <status></status>
        return False

    # skip 404 with status response 200
    response_length = node.getElementsByTagName("responselength")[0].firstChild.data
    if response_length == '6181':
        return False
    
    try:
        extension = node.getElementsByTagName("extension")[0].firstChild.data
        if extension in ['js', 'css', 'png']:
            return False    
    except:
        # Null => <extension></extension>
        return False

    # Skip other domain
    url = node.getElementsByTagName('url')[0].firstChild.data
    check_domain = 0
    for domain in white_list_domain:
        if domain in url:
            check_domain = 1
            break
    if not check_domain:
        return False

    return True


def parse_endpoint(xml_obj):
    host = xml_obj.getElementsByTagName('host')[0].firstChild.data
    port = xml_obj.getElementsByTagName('port')[0].firstChild.data
    protocol = xml_obj.getElementsByTagName('protocol')[0].firstChild.data
    url = '%s://%s:%s' % (protocol, host, port)
    method = xml_obj.getElementsByTagName('method')[0].firstChild.data
    path = xml_obj.getElementsByTagName('path')[0].firstChild.data
    raw_request = base64.b64decode(xml_obj.getElementsByTagName('request')[0].firstChild.data)
    raw_response = base64.b64decode(xml_obj.getElementsByTagName('response')[0].firstChild.data)
    #print(raw_response)
    return Endpoint(url, method, path, raw_request),raw_response

def main(infiles, outfile):
    endpoints = []
    headers = []
    args = Arguments().parse_args()
    meta = json.loads(open(args.meta_file).read())
    # throws exception on invalid format
    env.instrument_args = InstrumentArgs(meta)
    env.args = args
    #print(env.args)
    _node_iterator = NodeIterator()

    for infile in infiles:
        # use the parse() function to load and parse an XML file
        xml_obj = xml.dom.minidom.parse(infile)
        # print out the document node and the name of the first child tag
        items = xml_obj.getElementsByTagName("item")
        
        for item in items:
            if not condition_checker(item):
                continue
            
            ep,raw_response = parse_endpoint(item)
            #print(raw_response)
            if raw_response != None:
                raw_response_headers, raw_response_body = raw_response.split(b'\r\n\r\n', 1)
                # parse headers
                dict_headers = header2dict(raw_response_headers.decode())
                #print(dict_headers)


            request =  Node(ep.url,ep.methods)
            cfg = request.parse_instrumentation(dict_headers, '1')
            _node_iterator.add(request, cfg)

    #print(_node_iterator.total_cover_score)
    return _node_iterator
            

if __name__ == "__main__":
    infiles = [
        u"wfuzz/ffuf_14_06_01"
    ]
    outfile = './output/test'
    white_list_domain = ['dvpa.lab:8000']
    rs = main(infiles, outfile)
    print(rs.total_cover_score)