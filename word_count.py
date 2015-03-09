import logging
import re
from collections import defaultdict
from wikipedia import fetch_longest_contiguous, fetch_content, fetch_sitting_mps

def remove_references(text):
	# note: Anne Begg has <ref>{{ ... <!-- ... --> ... }}</ref>
	text = re.sub(ur"<ref[^<>]*>.*?<\s*/\s*ref\s*>", u" ", text, flags=re.U|re.I|re.DOTALL)
	text = re.sub(ur"<ref[^<>]*/>", u" ", text, flags=re.U|re.I)
	text = re.sub(ur"http://[^ <>]+", u" ", text, flags=re.U|re.I)
	# recent bot edits have changed this template a lot
	text = re.sub(re.escape(u"{{s-start}}") + ur".*?" + re.escape(u"{{s-end}}"), u" ", text, flags=re.U|re.I|re.DOTALL)
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

	logging.info("%s: https://en.wikipedia.org/w/index.php?title=%s&diff=%s&oldid=%s" % (title, title.replace(" ", "_"), recent_rev['revid'], old_rev['revid'],))

	return wc_diff(recent_wc, old_wc)

def differences_for_all_mps():
	differences = {}
	for mpname in fetch_sitting_mps():
		differences[mpname] = difference_in_content(mpname)
	return differences

def interesting_words(wc):
	return tuple((xw, xc) for (xw, xc) in sorted(wc.items(), key=lambda (yw, yc): yc, reverse=True) if len(xw) > 3)

if __name__=='__main__':
	logging.root.setLevel(logging.INFO)

	print "diffstat:"
	diffs = differences_for_all_mps()
	diffstats = list(
		(diffstat(wc), name)
		for name, wc in diffs.items())
	diffstats.sort(reverse=True, key=lambda ((a, d), n) : abs(a) + abs(d))
	for ((add, del_), name) in diffstats:
		print "% 4d % 4d %-30s %s" % (
			add, del_,
			("+" * (add//25)) + ("-" * (-del_//25)),
			name,)

	adds, dels = wc_sum(diffs.values())
	print "words added"
	print interesting_words(adds)[:50]
	print "words removed"
	print interesting_words(dels)[:50]

