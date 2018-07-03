#when other servers are down, try&except
#when a client send the same message to two dif servers at the same time
import asyncio
import logging
import sys
import urllib.parse
import time
import json
from datetime import datetime

SERVER_NAME_LIST = {'Alford','Ball','Hamilton','Holiday','Welsh'}

SERVER_ADDRESS_LIST = {
	'Alford':('localhost', 11000),
	'Ball':('localhost',11001),
	'Hamilton':('localhost',11002),
	'Holiday':('localhost',11003),
	'Welsh':('localhost',11004)}

PORT_NO = {
	'Alford':11000,
	'Ball':11001,
	'Hamilton':11002,
	'Holiday':11003,
	'Welsh':11004}

TALKTO = {
	'Alford':['Hamilton','Welsh'],
	'Ball':['Holiday','Welsh'],
	'Hamilton':['Holiday'],
	'Holiday':[],
	'Welsh':[]
}

COMTO = {
	'Alford':['Hamilton','Welsh'],
	'Ball':['Holiday','Welsh'],
	'Hamilton':['Alford','Holiday'],
	'Holiday':['Hamilton','Ball'],
	'Welsh':['Alford','Ball']
}

def isFloat(str):
	try:
		float(str)
		return True
	except:
		return False

def isInt(str):
	try:
		int(str)
		return True
	except:
		return False

class Server:

	def __init__(self, server_name,log):
		self.name = server_name
		self.IAmTalkee = {}
		self.IAmTalker = {}
		self.client_info ={}
		self.update = set()
		self.log = log

	@asyncio.coroutine
	def start_server_connection(self,talker):
		try:
			reader,writer = yield from asyncio.open_connection('localhost',PORT_NO[talker], loop=asyncio.get_event_loop())
		except:
			self.log.debug("Server {0} cannot connect to Server {1}".format(self.name, talker))
			yield from asyncio.sleep(5)
			asyncio.ensure_future(self.start_server_connection(talker),loop=asyncio.get_event_loop())
			return
		self.IAmTalker[talker] = (reader,writer)
		msg = "IAmServer {0}\n".format(self.name)
		writer.write(msg.encode())
		yield from writer.drain()
		self.log.debug("Server {0} connects to Server {1}".format(self.name, talker))
		asyncio.ensure_future(self.listen_to_server(talker,reader,writer))


	def IAmServer(self, msg_arr, reader, writer):
		if len(msg_arr) != 2:
			msg = (" ").join(msg_arr)
			handle_error(msg, "Incorrect format for server connection message",writer)
		talker_server = msg_arr[1]
		self.IAmTalkee[talker_server] = (reader,writer)
		self.log.debug("Server {0} got connected to Server {1}".format(self.name, talker_server))
		asyncio.ensure_future(self.listen_to_server(talker_server,reader,writer))
		return
		
	@asyncio.coroutine
	def reconnect_server(self, talker):
		if talker in TALKTO[self.name]:
			yield from asyncio.sleep(1)
			self.log.debug("Server {0} trying to connect with Server {1}".format(self.name, talker))
			asyncio.ensure_future(self.start_server_connection(talker))

	@asyncio.coroutine
	def listen_to_server(self, talker,reader,writer):
		while True:
			data = yield from reader.readline()
			if not data:
				self.log.debug("Server {0} is disconnected.".format(talker))
				if talker in self.IAmTalker:
					del self.IAmTalker[talker]
				elif talker in self.IAmTalkee:
					del self.IAmTalkee[talker]
				self.log.debug("Will stop sending updates to Server {0}.".format(talker))
				# yield from self.reconnect_server(talker)
				asyncio.ensure_future(self.reconnect_server(talker))
				break
			else:
				msg = data.decode()
				self.log.debug("Message: {0} received by Server {1} from Server {2}.".format(msg,self.name,talker))
				#handle AT message
				msg_arr = msg.split()
				if len(msg_arr) != 6:
					self.log.error("{0} Wrong number of arguments for AT message from Server, should be 6 instead.".format(msg))
				if self.checkShouldUpdate(msg, msg_arr):
					usrname = msg_arr[3]
					asyncio.ensure_future(self.updateServer(usrname,talker))


	@asyncio.coroutine
	def handle_connection(self,reader,writer):
		data = yield from reader.readline()
		msg = data.decode()
		#handle message
		msg_arr = msg.split()
		if len(msg_arr) == 0:
			self.handle_error(msg,"No argument",writer)
		else:
			self.log.debug("Message: {0} received.".format(msg))
			if msg_arr[0] == "IAmServer":
				self.IAmServer(msg_arr, reader, writer)
				yield from writer.drain()
			elif msg_arr[0] == "IAMAT":
				if self.IAMAT(msg, msg_arr, writer):
				#editting the AT message
					usrname = msg_arr[1]
					reply = self.client_info[usrname]
					asyncio.ensure_future(self.updateServer(usrname,"Client"))
				yield from writer.drain()
				writer.close()
			elif msg_arr[0] == "WHATSAT":
				yield from self.WHATSAT(msg,msg_arr, writer)
				yield from writer.drain()
				writer.close()
			else:
				self.handle_error(msg,"Wrong format, the message should start with IAMAT, AT or WHATSAT", writer)
				writer.close()


	def handle_error(self, msg, error,writer):
		writer.write("? {0}".format(msg).encode())
		self.log.error("Error: {0} The incorrect message is {1}.".format(error,msg))		

	def IAMAT(self, msg,msg_arr, writer):
		if len(msg_arr) != 4:
			self.handle_error(msg, "Wrong number of arguments for IAMAT message, should be 4 instead.",writer)
			return False
		#reply the client
		usrname = msg_arr[1]
		location = msg_arr[2]
		time_sent = msg_arr[3]
		if not isFloat(time_sent):
			self.handle_error(msg, "Wrong timestamp", writer)
			return False
		if not self.rightCords(location):
			self.handle_error(msg,"Wrong coordinates format.",writer)
			return False
		time_sent_float = float(time_sent)
		if time_sent_float < 0:
			self.handle_error(msg,"Timestamps must be positive.",writer)
			return False
		time_now_float = time.time()
		dif = time_now_float - time_sent_float
		time_diff_string = ""
		if dif > 0.0:
			time_diff_string = "+" + str(dif)
		else:
			time_diff_string = "-" + str(dif)
		part_reply = (" ").join(msg_arr[1:])
		reply = "AT "+ self.name +" "+time_diff_string+" "+ part_reply + "\n"
		writer.write(reply.encode())
		#check if should update
		if reply in self.update:
			self.log.debug("Same IAMAT message received before: {1}, not propagating".format(msg))
			return False
		time_sent_float = float(msg_arr[3])
		if msg_arr[1] in self.client_info:
			client_cache = self.client_info[usrname]
			client_cache_arr = client_cache.split()
			client_cache_time = client_cache_arr[5]
			client_cache_time_float = float(client_cache_time)
			if time_sent_float > client_cache_time_float:
				self.client_info[usrname] = reply
			else:
				return False
		self.client_info[usrname] = reply
		self.update.add(reply)
		return True
		

	@asyncio.coroutine
	def updateServer(self, usrname,talker):		
		#propagate to other servers
		reply = self.client_info[usrname]
		reply_b = reply.encode()
		self.log.debug("Updating servers.")
		for server in COMTO[self.name]:
			if server != talker:
				if server in self.IAmTalker:
					writer = self.IAmTalker[server][1]
					writer.write(reply_b)
					self.log.debug("Sending msg to Server {0}.".format(server))
					yield from writer.drain()
					self.log.debug("msg sent to {0}.".format(server))
				elif server in self.IAmTalkee:
					writer = self.IAmTalkee[server][1]
					writer.write(reply_b)
					self.log.debug("Sending msg to Server {0}.".format(server))
					yield from writer.drain()
					self.log.debug("msg sent to {0}.".format(server))

#for AT only, AT Alford +0.263873386 kiwi.cs.ucla.edu +34.068930-118.445127 1479413884.392014450
	def checkShouldUpdate(self, msg,msg_arr):
		if msg in self.update:
			self.log.debug("Same AT message received before: {0}, not propagating".format(msg))
			return False
		time_sent_float = float(msg_arr[5])
		usrname = msg_arr[3]
		if msg_arr[3] in self.client_info:
			client_cache = self.client_info[usrname]
			client_cache_arr = client_cache.split()
			client_cache_time = client_cache_arr[5]
			client_cache_time_float = float(client_cache_time)
			if time_sent_float > client_cache_time_float:
				self.client_info[usrname] = msg
			else:
				return False
		self.client_info[usrname] = msg
		self.update.add(msg)
		self.log.debug("AT message {0} updated.".format(msg))
		return True

	@asyncio.coroutine
	def WHATSAT(self, msg, msg_arr,writer):
		if len(msg_arr)!= 4:
			self.handle_error(msg,"Wrong number of arguments for WHATSAT. Should be 3.",writer)
		elif not isInt(msg_arr[2]):
			self.handle_error(msg, "The third argument for WHATSAT should be an int.",writer)
		elif not isInt(msg_arr[3]):
			self.handle_error(msg, "The fourth argument for WHATSAT should be an int.",writer)
		elif msg_arr[1] not in self.client_info:
			self.handle_error(msg, "There is no info regarding this username.", writer)
		else:
			usrname = msg_arr[1]
			num = int(msg_arr[2])
			rad = int(msg_arr[3])
			if num > 20 or num < 0:
				self.handle_error(msg, "The information bound shoule be a positive int smaller than 20.",writer)
			elif rad > 50 or rad < 0:
				self.handle_error(msg, "The radius shoule be a positive int smaller than 50.",writer)
			else:
				info = self.client_info[usrname]
				info_arr = info.split()
				location = info_arr[4]
				if not self.rightCords(location):
					self.handle_error(msg,"Wrong coordinates format.",writer)
				else:
					index = 0
					if location[0] == '+':
						index += location.find('-',1)
					else:
						index += location.find('+',1)
					lat = location[:index]
					lon = location[index:]
					yield from self.getGoogle(lat,lon,rad,num,writer,info)

	def rightCords(self, location):
		if location[0]!='+' and location[0]!='-':
			return False
		else:
			cnt_s = 0
			cnt_d = 0
			for digit in location:
				if not isInt(digit):
					if digit == '+' or digit == '-':
						cnt_s += 1
					elif digit == '.':
						cnt_d += 1
					else:
						return False
			if cnt_s != 2 or cnt_d !=2 :
				return False
		return True

#https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=34.068930%2C-118.445127&radius=10000&key=AIzaSyAzjRcJm1rHvQDIdCRAeztgqQOJ3kZomvU
	@asyncio.coroutine
	def getGoogle(self,lat,lon,rad,num,writer_o,info):
		if lat[0] =='+':
			lat = lat[1:]
		if lon[0] =='+':
			lon = lon[1:]
		location = lat +"," + lon
		url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+urllib.parse.quote(location)+"&radius="+str(rad*1000)+"&key=AIzaSyAzjRcJm1rHvQDIdCRAeztgqQOJ3kZomvU"
		url_p = urllib.parse.urlsplit(url.encode())
		reader,writer = yield from asyncio.open_connection(url_p.hostname, 443, ssl=True)
		
		#query = ('GET {path}?{query} HTTP/1.1\r\n' 'Host: {hostname}\r\n' '\r\n').format(path=url.path, hostname=url.hostname)
		query = b'GET %b?%b HTTP/1.1\r\nHost: %b\r\nConnection: close\r\n\r\n' % (url_p.path, url_p.query, url_p.hostname)
		writer.write(query)
		self.log.debug("GET request sent to Google on location ({0})".format(location))
		yield from writer.drain()
		yield from reader.readuntil(b'\r\n\r\n')
		response = (yield from reader.read()).decode()
		parsed = json.loads(response)
		if parsed['status'] == "OK":
			parsed['results'] = parsed['results'][:num]
			reply = json.dumps(parsed, indent=4)
			writer_o.write(info.encode())
			writer_o.write(reply.encode())
			writer_o.write(b'\r\n\r\n')

			yield from writer_o.drain()
		else:
			self.log.error("Error when acquiring info from Google at location ({0})".format(location))

def main():
	if len(sys.argv) != 2:
		sys.stderr.write("Wrong argument number {0}. Should be 2.\n".format(len(sys.argv)))
		exit(1)

	server_name = sys.argv[1]
	if server_name not in SERVER_NAME_LIST:
		sys.stderr.write("Invalid Server Name {0}\n".format(server_name))
		exit(1)

	logging.basicConfig(
	filename=server_name+'.log',
	level=logging.DEBUG,
	format='%(name)s: %(message)s')
	log = logging.getLogger(server_name)

	loop = asyncio.get_event_loop()
	ourServer = Server(server_name, log)
	coro = asyncio.start_server(ourServer.handle_connection, 'localhost',PORT_NO[server_name],loop=loop)
	asyncio.sleep(3)
	for talker in TALKTO[server_name]:
		asyncio.ensure_future(ourServer.start_server_connection(talker))
	server = loop.run_until_complete(coro)

	try:
		loop.run_forever()
	finally:
		loop.close()

if __name__ == "__main__":
	main()