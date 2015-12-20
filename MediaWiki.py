import json
from .ajax import ajax
from .Progress import Progress

class MediaWiki:
	def __init__(self, lang = 'ru'):
		self.__url = 'https://' + lang + '.wikipedia.org/w/api.php'

	def execQuery(self, query, onDone, onFail = (lambda e: None)):
		def onData(data):
			js = json.loads(data.decode('utf-8'))
			if 'error' in js:
				err = js['error']['info']
				onFail(err)
				sublime.error_message(err)
			else:
				onDone(js)

		ajax({
			'url': self.__url,
			'data': query,
			'done': onData,
			'fail': onFail
		})	


	def execQueryWithProgress(self, query, msg, onDone):
		pr = Progress(msg)

		def onMyDone(js):
			pr.stop()
			onDone(js)

		def onMyFail(err):
			pr.stop();

		self.execQuery(query, onMyDone, onMyFail)

	def search(self, query, onDone):
		self.execQueryWithProgress({
			'action': 'query',
			'list': 'search',
			'srlimit': 5,
			'srprop': '',
			'srredirects': 1,
			'format': 'json',
			'srsearch': query
		}, 'Searching', lambda js: onDone(list(map(lambda x: x['title'], js['query']['search']))))

	def preview(self, text, onDone):
		self.execQueryWithProgress({
			'action': 'parse',
			'text': text,
			'contentmodel': 'wikitext',
			'format': 'json'
		}, 'Building preview', lambda js: onDone(js['parse']['text']['*']))

	def getInterwiki(self, links, lang, onDone):
		limit = 50
		links = list(set(links)) # uniqify
		result = {}
		pr = Progress('Looking up...')

		def go(index):
			if index >= len(links):
				pr.stop()
				onDone(result)
			else:
				self.execQuery({
					'action': 'query',
					'prop': 'langlinks',
					'lllang': lang,
					'redirects': '',
					'lllimit': limit,
					'titles': '|'.join(links[index : index+limit]),
					'format': 'json',
				}, lambda json: onResult(json['query'], index), lambda err: pr.stop())

		def mapToDic(json, name):
			if (name in json):
				return dict(map(lambda m: (m['to'], m['from']), json[name]))
			else:
				return {}

		def onResult(json, index):
			redirects = dict(mapToDic(json, 'redirects'), **mapToDic(json, 'normalized'))
			for page in json['pages'].values():
				title = page['title']
				if ('langlinks' in page):
					result[redirects.get(title, title)] = page['langlinks'][0]['*']
			go(index + limit)

		go(0)
