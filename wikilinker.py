import sublime, sublime_plugin, re
from .snowball import RussianStemmer
from .MediaWiki import MediaWiki
from .tools import getSel, cmp_to_key

class WikilinkerCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):

		# invoked by callback
		if len(args) > 0:
			sel = sublime.Region(args['begin'], args['end'])
			self.view.replace(edit, sel, args['text'])
			return

		mw = MediaWiki()

		sel = getSel(self.view)
		text = self.view.substr(sel).strip()
		if (len(text) == 0):
			sublime.error_message('Nothing selected')
			return

		stem = RussianStemmer()
		text = text[0:100]
		text = re.sub(r'[—_\!\?\.\,\:«»\%\'\"]', ' ', text)
		text = re.sub(r' +', ' ', text).strip()
		words = re.split(' ', text)
		stemmedWords = list(map(lambda x: stem.stem(x), words[:3]))
		# append '*' to the first 3 words
		words = list(map(lambda x: x[0] if x[0].lower() == x[1].lower() else x[1], zip(words, stemmedWords))) + words[3:]

		def compare(x, y):
			def no_braces(str):
				ind = str.find(' (')
				return str if ind == -1 else str[:ind]
			xLen = len(no_braces(x))
			yLen = len(no_braces(y))
			if xLen != yLen:
				return xLen - yLen
			if len(x) != len(y):
				return len(x) - len(y)
			return 0 if x == y else (-1 if x < y else 1)

		def lowerFirst(str):
			return str[0].lower() + str[1:]

		def processResults(results):
			# special processing if only one word was selected
			if len(words) == 1:
				word = lowerFirst(words[0])[:3]
				sortedResults = sorted(results, key=cmp_to_key(compare))
				filtered = list(filter(lambda x: lowerFirst(x)[:3] == word, sortedResults))
				results = filtered + list(filter(lambda x: x not in filtered, results))

			self.view.show_popup_menu(results, lambda ind: onSelected(results, ind))

		def onSelected(results, ind):
			if (ind == -1):
				return
			res = results[ind];

			if len(res) <= len(text) and lowerFirst(text[:len(res)]) == lowerFirst(res):
				res = '[[' + text[:len(res)] + ']]' + text[len(res):]
			else:
				res = '[[' + res + '|' + text + ']]'

			self.view.run_command('wikilinker', { 'begin': sel.a, 'end': sel.b, 'text': res })

		mw.search(' '.join(words), processResults)
