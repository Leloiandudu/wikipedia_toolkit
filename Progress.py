import sublime

class Progress:
	def __init__(self, msg):
		self.msg = msg
		self.run = True
		self.pos = 0
		self.step()

	def step(self):
		if not self.run:
			sublime.status_message('')
			return
		sublime.status_message(self.msg + '.' * self.pos)
		self.pos += 1
		sublime.set_timeout(self.step, 500)

	def stop(self):
		self.run = False
