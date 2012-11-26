import collections
import re

class FileParser(object):

	REGEXP_SECTION = re.compile(r'^\s*\[(?P<name>[^]]+)\]\s*$')
	REGEXP_OPTION = re.compile(r'^(?P<name>.+?)(?P<operator>[+]?=)(?P<value>.*)$')

	def __init__(self, dict_type=None):
		if dict_type is not None:
			self._dict_type = dict_type
		else:
			self._dict_type = collections.OrderedDict

		self._options = None

	def _create_dict(self):
		return self._dict_type()

	def parse(self, filename):
		self._options = self._create_dict()
		self._current_section = None

		with open(filename) as config_file:
			line_number = 0
			for line in map(lambda line: line.rstrip(), config_file):
				line_number += 1
				if not self._parse_line(line):
					# TODO: custom exception
					raise Exception("Error in '%s' at line %d." % (filename, line_number))

	def _parse_line(self, line):
		# skip empty lines or comments
		if len(line) == 0 or line[0] in ["#", ";"]:
			return True

		# sections
		match = self.REGEXP_SECTION.match(line)
		if match is not None:
			self._current_section = match.group("name").strip()
			self._options[self._current_section] = self._create_dict()
			return True

		# option, value
		match = self.REGEXP_OPTION.match(line)
		if match is not None:
			option = match.group("name").strip()
			operator = match.group("operator")
			value = match.group("value").strip()
			if operator == "=":
				self._options[self._current_section][option] = value
			elif operator == "+=":
				if not option in self._options[self._current_section]:
					self._options[self._current_section][option] = []
				elif type(self._options[self._current_section][option]) is not list:
					self._options[self._current_section][option] = [self._options[self._current_section][option]]
				self._options[self._current_section][option].append(value)
			else:
				raise NotImplementedError("Unexpected operator.")
			return True

		return False
