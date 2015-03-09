import logging
import re
from collections import defaultdict
from wikipedia import fetch_longest_contiguous, fetch_content, fetch_sitting_mps

def remove_references(text):
	text = re.sub(ur"<ref[^<>]*>[^<>]*</ref>", u"", text, flags=re.U|re.I)
	text = re.sub(ur"<ref[^<>]*/>", u"", text, flags=re.U|re.I)
	return text

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

def wc_sum(wc_list):
	adds = defaultdict(int)
	dels = defaultdict(int)
	for wc in wc_list:
		for k, v in wc.items():
			if v > 0:
				adds[k] += v
			else:
				dels[k] += -v
	return dict(adds), dict(dels)

def diffstat(wc):
	adds = sum(v for v in wc.values() if v > 0)
	dels = sum(v for v in wc.values() if v < 0)
	return adds, dels


def difference_in_content(title):
	recent_rev = fetch_longest_contiguous(title, "2015-02-01", "2015-03-01")
	recent_wikitext = fetch_content(title, recent_rev['revid'])
	recent_wc = word_count(remove_references(recent_wikitext))

	old_rev = fetch_longest_contiguous(title, "2014-08-01", "2014-09-01")
	old_wikitext = fetch_content(title, old_rev['revid'])
	old_wc = word_count(remove_references(old_wikitext))

	return wc_diff(recent_wc, old_wc)

def differences_for_all_mps():
	differences = {}
	for mpname in fetch_sitting_mps()[:50]:
		differences[mpname] = difference_in_content(mpname)
	return differences

if __name__=='__main__':
	logging.root.setLevel(logging.INFO)

	print "diffstat:"
	diffs = differences_for_all_mps()
	for name, wc in diffs.items():
		print diffstat(wc), name

	adds, dels = wc_sum(diffs.values())
	print "words added"
	print tuple(sorted(adds.items(), key=lambda (w, c): c, reverse=True))[:20]
	print "words removed"
	print tuple(sorted(dels.items(), key=lambda (w, c): c, reverse=True))[:20]

