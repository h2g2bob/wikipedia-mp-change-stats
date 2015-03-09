import logging
import datetime
from fetch import fetch_wikipedia_api

def revisions(title, start, end):
	revisions = []
	cont = {}
	while True:
		data = fetch_wikipedia_api(
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
		)
		page, = data['query']['pages'].values()
		revisions += page.get('revisions', [])

		if u'query-continue' in data:
			cont = {"rvcontinue" : str(data[u'query-continue'][u'revisions'][u'rvcontinue'])}
		else:
			break
	return revisions

def fetch_first_revision_before(title, end):
	data = fetch_wikipedia_api(
		action=u"query",
		prop=u"revisions",
		titles=title,
		rvlimit=u"1",
		rvprop=u"ids|timestamp",
		format=u"json",
		rvstart=end + "T00:00:00Z",
		rvdir=u"older",
	)
	page, = data['query']['pages'].values()
	rev, = page['revisions']
	return rev

def fetch_content(title, revid):
	data = fetch_wikipedia_api(
		action=u"query",
		prop=u"revisions",
		titles=title,
		rvlimit=u"1",
		rvprop=u"ids|timestamp|content",
		format=u"json",
		rvstartid=unicode(revid),
		rvendid=unicode(revid),
	)
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

