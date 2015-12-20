import sublime, sublime_plugin, re
from .MediaWiki import MediaWiki

class InterwikiCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		text = self.view.substr(sublime.Region(0, self.view.size()))
		links = list(map(
			lambda match: (match.group(1), match.start(1)), 
			re.finditer(r'\[\[([^\]\|]+)(?:\|(.+?))?\]\]', text)
		))

		if ('interLinks' not in args):
			MediaWiki(args.get('lang', 'en')).getInterwiki(
				map(lambda link: link[0], links), 
				'ru', 
				lambda interLinks: self.view.run_command('interwiki', { 'interLinks': interLinks })
			)
			return

		offset = 0
		interLinks = args['interLinks']
		for link, index in links:
			if link in interLinks:
				newLink = interLinks[link];
				sel = sublime.Region(index+offset, index+offset+len(link))
				self.view.replace(edit, sel, newLink)
				offset += len(newLink) - len(link)
