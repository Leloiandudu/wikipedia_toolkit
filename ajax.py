import urllib.request, urllib.parse, urllib.error, threading, sublime

def ajax(ajax):
	class Task(threading.Thread):
		def __init__(self, cb):
			self.cb = cb
			threading.Thread.__init__(self)

		def run(self):
			self.cb()
	
	def work():
		try:
			url = ajax['url'];
			data = None
			if 'data' in ajax: 
				data = urllib.parse.urlencode(ajax['data']).encode("UTF-8")
			request = urllib.request.Request(url, data)
			http_file = urllib.request.urlopen(request)
			if ('done' in ajax):
				ajax['done'](http_file.read())
			return
		except (urllib.error.HTTPError) as e:
			err = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
		except (urllib.error.URLError) as e:
			err = '%s: URL error %s contacting API' % (__name__, str(e.reason))
		if ('fail' in ajax):
			ajax['fail'](err)
		sublime.error_message(err)
		return

	Task(work).start()