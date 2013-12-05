#!/usr/bin/env python

# User details
# Add the url to your feed. NOTE: This has only been tested on the favourites feed from tvtorrents.com but it should work with other feeds
feed_url = "enter your feed url here"
hist = "/downloads/logs/rss/rss-hist.txt"		# Location of history file
inc = "/downloads/logs/rss/rss-inc.txt"		# Location of incoming links file
diff = "/downloads/logs/rss/rss-diff.txt"		# Location of difference file. 

# Transmission RPC details
# Fill in your transmission details below
USER = 'username'		# Username
PASS = 'password'		# Password
HOST = 'localhost'		# The remote host
PORT = '9091'			# The same port as used by the server

# ------------------------------------------------------------------------------------------------------------------
# DO NOT MODIFY BELOW THIS LINE UNLESS YOU KNOW WHAT YOU ARE DOING!!
# ------------------------------------------------------------------------------------------------------------------

# Import some needed libraries
import feedparser
import difflib
import urllib
import urllib2
import transmissionrpc
import os

# Create the log files if they do not exist. This will prevent read/write errors later on
if not os.path.exists(hist):
    file(hist, 'w').close()
if not os.path.exists(inc):
    file(inc, 'w').close()
if not os.path.exists(diff):
    file(diff, 'w').close()

# Parse the feed url given in the user details section.
feed = feedparser.parse(feed_url)
# Strip all the unnecessary data and grab the links 
with open(inc, 'w+') as incoming_file:
	for post in feed.entries:
		incoming_file.write(post.link + "\n")
		#post.title
		#post.link
		#post.comments
		#post.pubDate

# Check the incoming file against the history file. If there is a differece, write it to the diff file. 
def build_set(inc):
    # A set stores a collection of unique items.  Both adding items and searching for them
    # are quick, so it's perfect for this application.
    found = set()

    with open(inc) as incoming:
        for line in incoming:
            # [:2] gives us the first two elements of the list.
            # Tuples, unlike lists, cannot be changed, which is a requirement for anything
            # being stored in a set.
            found.add(tuple(sorted(line.split()[:2])))

    return found

set_more = build_set(inc)
set_del = build_set(hist)

with open(diff, 'w+') as difference:
   # Using with to open files ensures that they are properly closed, even if the code
   # raises an exception.

   for res in (set_more - set_del):
      # The - computes the elements in set_more not in set_del.
      difference.write(" ".join(res) + "\n") 

# Use contents of diff file and add them to transmission via the rpc
# Connect to the transmission RPC server
tc = transmissionrpc.Client(HOST, port=PORT, user=USER, password=PASS)
# Open the diff file and add the contents (links) to transmission
f = open(diff)
for line in iter(f):
	# Add torrents to transmission via the rpc
	tc.add_torrent(line)
f.close()

# Move contents of diff file and append to history file, then reset diff file
# Open diff file, read contents then close file
diff_file = open(diff, "r")
diff_data = diff_file.read()
diff_file.close()
# Open history file and appaend diff file data
hist_file = open(hist, "a")
hist_file.write(diff_data)
hist_file.close()

# Now we have finished with the diff and inc files, we open them, write in nothing and resave the file
open(diff, 'w').close()
open(inc, 'w').close()