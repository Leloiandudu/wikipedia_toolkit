import sublime, sublime_plugin, tempfile, io, os, webbrowser;
from .MediaWiki import MediaWiki
from .tools import getSel

class WikiPreviewCommand(sublime_plugin.TextCommand):
	templateArg = '***WIKITEXT***'
	template = '''
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<base href="http://ru.wikipedia.org/">
<link rel="stylesheet" href="https://bits.wikimedia.org/ru.wikipedia.org/load.php?debug=false&amp;lang=ru&amp;modules=ext.flaggedRevs.basic%7Cext.gadget.collapserefs%2CdirectLinkToCommons%2CreferenceTooltips%7Cext.rtlcite%2Cwikihiero%7Cext.uls.nojs%7Cext.visualEditor.viewPageTarget.noscript%7Cmediawiki.legacy.commonPrint%2Cshared%7Cmw.PopUpMediaTransform%7Cskins.vector&amp;only=styles&amp;skin=vector&amp;*" />
<link rel="stylesheet" href="//bits.wikimedia.org/ru.wikipedia.org/load.php?debug=false&amp;lang=ru&amp;modules=site&amp;only=styles&amp;skin=vector&amp;*" />
<div style="margin: 10px">
<div id="bodyContent">
***WIKITEXT***
</div>
</div>
'''
	def run(self, edit, all):
		mw = MediaWiki()

		if all:
			text = self.view.substr(sublime.Region(0, self.view.size()))
		else:
			text = self.view.substr(getSel(self.view)).strip()

		if (len(text) == 0):
			sublime.error_message('Nothing selected')
			return

		def onDone(html):
			html = self.template.replace(self.templateArg, html)
			name = tempfile.gettempdir() + '\\wiki-preview%s.htm' % self.view.buffer_id()
			print(name)
			tmpFile = io.open(name, 'wb')
			tmpFile.write(html.encode('UTF-8'));
			tmpFile.close()
			webbrowser.open('file:///' + name.replace('\\', '/'))
			sublime.set_timeout(lambda: os.remove(name), 2000)

		mw.preview(text, onDone)
