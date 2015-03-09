import logging
import urllib
import json
import hashlib
import os.path

def encode(**kw):
	return "&".join(
		"%s=%s" % (k, urllib.quote(v.encode("utf8")))
		for (k, v) in kw.items())

def fetch(url):
	fname = os.path.join("www-cache", hashlib.sha1(url).hexdigest())
	logging.debug("fetch(%r) -> %r", url, fname)
	try:
		with open(fname, "r") as f:
			return f.read()
	except IOError:
		data = fetch_nocache(url)
		with open(fname, "w") as f: # NOT threadsafe
			f.write(data)
		with open(fname + ".url", "w") as f:
			f.write(url)
		return data

def fetch_nocache(url):
	logging.debug("fetch_nocache(%r)", url)
	return urllib.urlopen(url).read()

def fetch_json(url):
	return json.loads(fetch(url))

def fetch_wikipedia_api(**kw):
	return fetch_json("https://en.wikipedia.org/w/api.php?" + encode(**kw))

