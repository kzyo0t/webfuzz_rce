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
    headers[line[:split_here]] = line[split_here:]
  return headers
data=b"HTTP/1.1 200 OK\r\nDate: Tue, 13 Jun 2023 03:56:40 GMT\r\nServer: Apache/2.4.52 (Ubuntu)\r\nSet-Cookie: PHPSESSID=1ot13m2r8449jaj7kongcqcjdq; path=/\r\nExpires: Thu, 19 Nov 1981 08:52:00 GMT\r\nCache-Control: no-store, no-cache, must-revalidate\r\nPragma: no-cache\r\nI-87750866: 1\r\nI-50143718: 1\r\nVary: Accept-Encoding\r\nContent-Length: 654\r\nConnection: close\r\nContent-Type: text/html; charset=UTF-8"
print(header2dict(data.decode()))