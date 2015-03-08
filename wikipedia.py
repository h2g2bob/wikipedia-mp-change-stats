import logging
import json
import urllib
import json
import os.path
import hashlib
import datetime
import re
from collections import defaultdict

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

def revisions(title, start, end):
	revisions = []
	cont = {}
	while True:
		data = fetch_json("https://en.wikipedia.org/w/api.php?" + encode(
			action=u"query",
			prop=u"revisions",
			titles=title,
			rvlimit=u"5",
			rvprop=u"ids|timestamp",
			format=u"json",
			rvstart=start + "T00:00:00Z",
			rvend=end + "T00:00:00Z",
			rvdir=u"newer",
			**cont
		))
		page, = data['query']['pages'].values()
		revisions += page.get('revisions', [])

		if u'query-continue' in data:
			cont = {"rvcontinue" : str(data[u'query-continue'][u'revisions'][u'rvcontinue'])}
		else:
			break
	return revisions

def fetch_first_revision_before(title, end):
	data = fetch_json("https://en.wikipedia.org/w/api.php?" + encode(
		action=u"query",
		prop=u"revisions",
		titles=title,
		rvlimit=u"1",
		rvprop=u"ids|timestamp",
		format=u"json",
		rvstart=end + "T00:00:00Z",
		rvdir=u"older",
	))
	page, = data['query']['pages'].values()
	rev, = page['revisions']
	return rev

def fetch_content(title, revid):
	data = fetch_json("https://en.wikipedia.org/w/api.php?" + encode(
		action=u"query",
		prop=u"revisions",
		titles=title,
		rvlimit=u"1",
		rvprop=u"ids|timestamp|content",
		format=u"json",
		rvstartid=unicode(revid),
		rvendid=unicode(revid),
	))
	page, = data['query']['pages'].values()
	rev, = page['revisions']
	return rev['*']



def longest_contiguous(revisions):
	durations_and_data = []
	for oldrev, newrev in zip(revisions[:-2], revisions[1:]):
		olddt = datetime.datetime.strptime(oldrev['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
		newdt = datetime.datetime.strptime(newrev['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
		durations_and_data.append((newdt - olddt, oldrev))
	durations_and_data.sort()
	longest_rev = durations_and_data[-1]
	return longest_rev[1]
	
def fetch_longest_contiguous(title, start, end):
	revs = revisions(title, start, end)
	if len(revs) == 0:
		return fetch_first_revision_before(title, end)
	elif len(revs) == 1:
		return revs[0]
	else:
		return longest_contiguous(revs)

def word_count(text):
	words = defaultdict(int)
	for word in re.findall(ur"\b(\w+)\b", text, flags=re.U):
		words[word] += 1
	return dict(words)

def wc_diff(a, b):
	diffs = {}
	for k in set(a.keys()) | set(b.keys()):
		n = a.get(k,0) - b.get(k,0)
		if n != 0:
			diffs[k] = n
	return diffs

def difference_in_content(title):
	recent_rev = fetch_longest_contiguous(title, "2015-02-01", "2015-03-01")
	recent_wikitext = fetch_content(title, recent_rev['revid'])
	recent_wc = word_count(recent_wikitext)

	old_rev = fetch_longest_contiguous(title, "2014-08-01", "2014-09-01")
	old_wikitext = fetch_content(title, old_rev['revid'])
	old_wc = word_count(old_wikitext)

	return wc_diff(old_wc, recent_wc)

if __name__=='__main__':
	logging.root.setLevel(logging.DEBUG)
	print difference_in_content(u"David Amess")

