import sublime, sublime_plugin
import os
import fileinput
import shutil
import functools

class Settings():

	def __init__(self):
		
		#Initialize settings
		settings = sublime.load_settings("Remote Directory.sublime-settings")

		self.settings = {}

		self.settings['local_mask'] = ""
		self.settings['remote_mask'] = ""
		self.settings['history_file'] = ""
		self.settings['exclude_directories'] = []
		self.settings['exclude_extensions'] = []
		self.settings['debug'] = False

		# Get project specific settings (legacy)
		local_path_mask = sublime.active_window().active_view().settings().get("local_path_mask", settings.get("local_path_mask", ""))
		remote_path_mask = sublime.active_window().active_view().settings().get("remote_path_mask", settings.get("remote_path_mask", ""))
		history_file_name = sublime.active_window().active_view().settings().get("history_file_name", settings.get("history_file_name", "sublime_gethistory.txt"))

		self.settings['local_mask'] = local_path_mask
		self.settings['remote_mask'] = remote_path_mask
		self.settings['history_file'] = history_file_name

		# Get project specific settings from remote_directory object
		remote_directory = sublime.active_window().active_view().settings().get("remote_directory", None)

		if remote_directory:
			for item in remote_directory:
				self.settings[item] = remote_directory[item]

		# Remove trailing slashes off local and remote masks
		if self.settings['local_mask'].endswith('/') or self.settings['local_mask'].endswith('\\'):
			self.settings['local_mask'] = self.settings['local_mask'][:-1]
		if self.settings['remote_mask'].endswith('/') or self.settings['remote_mask'].endswith('\\'):
			self.settings['remote_mask'] = self.settings['remote_mask'][:-1]

	def get(self, key):
		return self.settings.get(key, "")

class History():
	history_file_path = ""

	def __init__(self, history_file_path, debug):

		self.history_file_path = history_file_path
		self.debug = debug

		# Check to see if file already exists
		if not os.access(self.history_file_path, os.F_OK):
			self.create_history_file()

	def create_history_file(self):

		if not os.access(self.history_file_path, os.F_OK):
			self.print_message ("create_history_file: Creating history file at '" + self.history_file_path + "'")
			history_file = open(self.history_file_path, 'a')
			history_file.close()

	def get_date_modified(self, file_name):

		history_file = open(self.history_file_path, 'r')
		file_found = False

		for line in history_file:
			if not line.split():
				continue
			else:
				tokens = line.split("@")

				if len(tokens) == 2 and tokens[0] == file_name:
					file_found = True
					break

		history_file.close()

		if file_found:
			self.print_message("get_date_modified: " + file_name + " " + tokens[1])
			return float(tokens[1])
		else:
			self.print_message("get_date_modified: " + file_name + " -1")
			return -1

	def update_history(self, file_name, last_modified):
		self.print_message("update_history: Updating...")
		new_line = file_name + "@" + str(last_modified) + "\n"
		file_found = False

		for line in fileinput.input(self.history_file_path, inplace=1):
			if not line.split():
				continue
			else:
				tokens = line.split("@")

				if len(tokens) == 2 and tokens[0] == file_name:
					file_found = True
					print(new_line)
				else:
					print(line)

		if not file_found:
			history_file = open(self.history_file_path, 'a')
			history_file.write(new_line)
			history_file.close()

	def print_message(self, message):

		if self.debug:
			print(message)

class RemoteDirectory():

	def __init__(self):
		self.settings = Settings()

	def get_file(self, remote_file):

		self.print_message("get_file: " + remote_file)
		local_file = self.get_directory_from_path_mask(remote_file, self.settings.get("remote_mask"), self.settings.get("local_mask"))

		if local_file == -1:
			self.print_message("get_file: Skipping file")
			return

		local_file_path = os.path.split(local_file)
		remote_file_path = os.path.split(remote_file)

		if not self.is_file_valid(remote_file):
			return

		# Make sure the local directory exists - This shouldn't really happen but whatever
		self.create_directory(local_file_path[0])

		history_file_path = os.path.join(local_file_path[0], self.settings.get("history_file"))
		history = History(history_file_path, self.settings.get("debug"))

		if not os.path.isdir(remote_file):
			#We can't get a file if it isn't there
			if os.access(remote_file, os.F_OK):
				last_modified = os.stat(remote_file).st_mtime
			else:
				self.print_message("get_file: File '" + remote_file_path[1] + "' not found. Aborting.")
				return

			# Get the file
			shutil.copy2(remote_file, local_file)

			# Update the history file
			history.update_history(local_file_path[1], last_modified)

			self.print_message("get_file: GET '" + local_file_path[1] + "' completed successfully")
		else:
			# We need to get all the files in the directory and call get_file on those
			for root, dirs, files in os.walk(remote_file):
				for f in files:

					remote_file = os.path.join(root, f)

					if remote_file != -1:
						self.get_file(remote_file)
						

	def put_file(self, local_file):

		self.print_message("put_file: " + local_file)
		local_file_path = os.path.split(local_file)
		remote_file = self.get_directory_from_path_mask(local_file, self.settings.get("local_mask"), self.settings.get("remote_mask"))
		
		if remote_file == -1:
			self.print_message("put_file: File not part of mask. Aborting.")
			return

		remote_file_path = os.path.split(remote_file)

		if not self.is_file_valid(local_file):
			return

		# Make sure directory exists
		self.create_directory(remote_file_path[0])

		history_file_path = os.path.join(local_file_path[0], self.settings.get("history_file"))
		history = History(history_file_path, self.settings.get("debug"))
		last_modified = 0

		# If we're not trying to PUT a directory
		if not os.path.isdir(local_file):
			if os.access(remote_file, os.F_OK):
				self.print_message("put_file: " + remote_file + " exists.")
				last_modified = os.stat(remote_file).st_mtime
				history_last_modified = history.get_date_modified(local_file_path[1])

				if last_modified > history_last_modified:
					self.print_message("put_file: last_modified: " + str(last_modified) + " history: " + str(history_last_modified))
					self.print_message("put_file: Remote file is newer than local. Aborting.")

					# FIXME Checking to make sure that local and remote mask have been initialized
					if self.settings.get("local_mask") != self.settings.get("remote_mask"):
						sublime.message_dialog("Aborting PUT: Remote file is newer than local. GET first.")

					return -1

			shutil.copy2(local_file, remote_file)

			# if not last_modified:
			last_modified = os.stat(remote_file).st_mtime
			history.update_history(local_file_path[1], last_modified)

			self.print_message("put_file: PUT '" + local_file_path[1] + "' completed successfully")

			return
		else:
			# We need to put all the subdirectories and files into the remote
			for root, dirs, files in os.walk(local_file):
				for f in files:

					local_file = os.path.join(root, f)

					if local_file != -1:
						self.put_file(local_file)

	def get_directory_from_path_mask(self, file, mask, new_mask):

		file_path = os.path.split(file)
		path_index = file_path[0].find(mask)

		if path_index == -1:
			if file == mask:
				self.print_message("get_directory_from_path_mask: " + new_mask)
				return new_mask
			else:
				self.print_message("get_directory_from_path_mask: Path does not contain mask")
				return -1

		path_index += len(mask)

		self.print_message("get_directory_from_path_mask: " + os.path.join(new_mask + file_path[0][path_index:], file_path[1]))
		return os.path.join(new_mask + file_path[0][path_index:], file_path[1])

	def is_file_valid(self, file_path):

		# Check our exclusions against file
		exclude_directories = self.settings.get("exclude_directories")
		exclude_extensions = self.settings.get("exclude_extensions")

		file_path = os.path.split(file_path)

		for dir in exclude_directories:
			if dir in file_path[0]:
				self.print_message("is_file_vaild: File '" + file_path[1] + "' is in excluded path")
				return False

		for ext in exclude_extensions:
			if file_path[1].endswith(ext):
				self.print_message("is_file_valid: File '" + file_path[1] + "' contains an excluded extension")
				return False

		return True

	def create_directory(self, path):

		if not os.path.exists(path):
			if os.path.isfile(path):
				os.makedirs(os.path.split(path)[0])
			else:
				os.makedirs(path)

	def print_message(self, message):

		if self.settings.get("debug"):
			print(message)

class getCommand(sublime_plugin.TextCommand):
	def run(self, edit):

		rd = RemoteDirectory()
		local_file = self.view.file_name()
		remote_file = rd.get_directory_from_path_mask(local_file, rd.settings.get("local_mask"), rd.settings.get("remote_mask"))
		rd.print_message("get: " + remote_file)

		if remote_file != -1:
			rd.get_file(remote_file)

			# Revert
			sublime.set_timeout(functools.partial(self.view.run_command, "revert"), 0)

class put(sublime_plugin.EventListener):
	def on_post_save(self, view):

		rd = RemoteDirectory()
		local_file = view.file_name()
		rd.print_message("put: " + local_file)
		status = rd.put_file(local_file)

		# Not sure if this is what we want
		if status == -1:
			view.run_command("revert")
			return

class putCommand(sublime_plugin.TextCommand):
	def run(self, edit):

		rd = RemoteDirectory()
		local_file = self.view.file_name()
		rd.print_message("put: " + local_file)
		rd.put_file(local_file)

class get_filesCommand(sublime_plugin.WindowCommand):
	def run(self, files):

		rd = RemoteDirectory()
		rd.print_message("get_files: [" + ', '.join(files) + "]")
		
		for file in files:
			remote_file = rd.get_directory_from_path_mask(file, rd.settings.get("local_mask"), rd.settings.get("remote_mask"))

			if remote_file != -1:
				rd.get_file(remote_file)

	def is_visible(self, files):
		return len(files) > 0

class get_dirsCommand(sublime_plugin.WindowCommand):
	def run(self, dirs):

		rd = RemoteDirectory()
		rd.print_message("get_dirs: [" + ', '.join(dirs) + "]")

		for dir in dirs:
			remote_file = rd.get_directory_from_path_mask(dir, rd.settings.get("local_mask"), rd.settings.get("remote_mask"))

			if remote_file != -1:
				rd.get_file(remote_file)


	def is_visible(self, dirs):
		return len(dirs) > 0

class put_filesCommand(sublime_plugin.WindowCommand):
	def run(self, files):

		rd = RemoteDirectory()
		rd.print_message("put_files: [" + ', '.join(files) + "]")

		for file in files:
			rd.put_file(file)

	def is_visible(self, files):
		return len(files) > 0

class put_dirsCommand(sublime_plugin.WindowCommand):
	def run(self, dirs):

		rd = RemoteDirectory()
		rd.print_message("put_dirs: [" + ', '.join(dirs) + "]")

		for dir in dirs:
			rd.put_file(dir)

	def is_visible(self, dirs):
		return len(dirs) > 0