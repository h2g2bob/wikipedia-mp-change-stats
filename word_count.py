import logging
import re
from collections import defaultdict
from wikipedia import fetch_longest_contiguous, fetch_content

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

