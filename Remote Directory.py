import sublime, sublime_plugin
import os
import shutil
import fileinput
import re
from subprocess import check_call

class putCommand(sublime_plugin.EventListener):
	def on_post_save(self, view):
		settings = sublime.load_settings("Remote Directory.sublime-settings")
		#If project settings are defined, use them, otherwise, use the package settings, otherwise, default
		local_path_mask = sublime.active_window().active_view().settings().get("local_path_mask", settings.get("local_path_mask", ""))
		local_file_path = os.path.split(view.file_name())
		local_file_index = local_file_path[0].find(local_path_mask)

		if local_file_index == -1:
			#sublime.message_dialog("The local_path_mask is invalid for the current file. GET aborted.")
			print local_path_mask
			return
		
		local_file_index += len(local_path_mask)

		remote_path_mask = sublime.active_window().active_view().settings().get("remote_path_mask", settings.get("remote_path_mask", ""))
		remote_file_path = remote_path_mask + view.file_name()[local_file_index:]

		#sublime.message_dialog(remote_file_path)

		if os.access(remote_file_path, os.F_OK):
			#last_modified refers to the last time the file was changed
			last_modified = os.stat(remote_file_path).st_mtime
			#sublime.message_dialog(repr(last_modified))

			historypath = local_file_path[0] + "\\" + settings.get("history_file_name", "sublime_gethistory.txt") 

			#Check to see if the sublime_gethistory file exists
			if os.access(historypath, os.F_OK):
				#File Exists! Time to read!
				historyfile = open(historypath, 'r')

				#Each line in history file looks like @filename@lastmodified
				for line in historyfile:
					if not line or line.isspace():
						continue
					else:
						tokens = line.split("@")

						#sublime.message_dialog(tokens[1] + " - " + local_file_path[1])

						if tokens[1] == local_file_path[1]:
							#This is the line we're looking for!
							if float(tokens[2]) == last_modified:
								#They match! We're good to PUT!
								#sublime.message_dialog("Match found! We're good to PUT!")

								shutil.copy2(view.file_name(), remote_file_path)
								historyfile.close()
								
								#Update the last_modified in the file
								newline = "@" + local_file_path[1] + "@" + repr(os.stat(remote_file_path).st_mtime)

								for line in fileinput.input(historypath, inplace=True): 
									if not line or line.isspace():
										continue
									else:
										tokens = line.split("@")

										if tokens[1] == local_file_path[1]:
											print line.replace(line, newline)
										else:
											print line
											
								fileinput.close()

								print "Put operation completed successfully"
								return
							else:
								#They don't match! Fail!
								sublime.message_dialog("Cannot put because the remote file is newer than the local file. Get remote file first.")

								#Get the last time the local file was modified
								local_lastModified = os.stat(view.file_name()).st_mtime

								#Now we need to perform the put anyways
								if local_lastModified < os.stat(view.file_name()).st_mtime:
									shutil.copy2(view.file_name(), remote_file_path)
									historyfile.close()
									
									#Update the last_modified in the file
									newline = "@" + local_file_path[1] + "@" + repr(os.stat(remote_file_path).st_mtime)

									for line in fileinput.input(historypath, inplace=True): 
										if not line or line.isspace():
											continue
										else:
											tokens = line.split("@")

											if tokens[1] == local_file_path[1]:
												print line.replace(line, newline)
											else:
												print line
												
									fileinput.close()

									print "Put operation completed successfully"
								else:
									print "Put operation cancelled"

								sublime.active_window().active_view().run_command('revert')
								return
				else:
					sublime.message_dialog("Remote file already exists. Need to get file before it can be put")
					return
			else:
				#File Does Not Exist! Failure!
				sublime.message_dialog("Cannot put because the remote file is newer than the local file. get first.")
				return
				
		else:
			#File doesn't exist on the remote server. PUT it
			shutil.copy2(view.file_name(), remote_file_path)

			#Record the new last_modified in sublime_gethistory
			last_modified = os.stat(remote_file_path).st_mtime
			historypath = local_file_path[0] + "\\" + settings.get("history_file_name", "sublime_gethistory.txt") 
			newline = "@" + local_file_path[1] + "@" + repr(last_modified) + "\n"

			historyfile = open(historypath, 'a')
			historyfile.write(newline)
			historyfile.close()

			print "Put operation completed successfully"
			return


class getCommand(sublime_plugin.TextCommand):
	def run_(self, args):
		self.view.window().run_command("get_file", self.view.file_name())

class get_fileCommand(sublime_plugin.WindowCommand):
	def run_(self, f):
		settings = sublime.load_settings("Remote Directory.sublime-settings")
		#Example base directory. Real would be C:\Users\username\Documents\programs\
		local_path_mask = sublime.active_window().active_view().settings().get("local_path_mask", settings.get("local_path_mask", ""))
		local_file_path = os.path.split(f)
		local_file_index = local_file_path[0].find(local_path_mask)

		if local_file_index == -1:
			sublime.message_dialog("The local_path_mask(" + local_path_mask + ") is invalid for the current file. Get operation aborted.")
			return
	
		local_file_index += len(local_path_mask)

		remote_path_mask = sublime.active_window().active_view().settings().get("remote_path_mask", settings.get("remote_path_mask", ""))
		remote_file_path = remote_path_mask + f[local_file_index:]

		#sublime.message_dialog(remote_file_path)

		if os.access(remote_file_path, os.F_OK):
			historypath = local_file_path[0] + "\\" + settings.get("history_file_name", "sublime_gethistory.txt") 

			if not os.access(historypath, os.F_OK):
				print "Created history file at \"" + historypath + "\""
				historyfile = open(historypath, 'a')
				historyfile.close()

			#Each line in history file looks like @filename@lastmodified
			newline = "@" + local_file_path[1] + "@" + repr(os.stat(remote_file_path).st_mtime)

			filefound = False

			for line in fileinput.input(historypath, inplace=True): 
				if not line or line.isspace():
					continue
				else:
					tokens = line.split("@")

					if tokens[1] == local_file_path[1]:
						filefound = True
						print line.replace(line, newline)
					else:
						print line

			fileinput.close()

			if not filefound:
				historyfile = open(historypath, 'a')
				historyfile.write(newline)
				historyfile.close()

			#Ok, copy the file from the remote directory to the local directory
			local_path = local_path_mask + f[local_file_index:]
			shutil.copy2(remote_file_path, local_path)

			sublime.active_window().active_view().run_command('revert')
			print "Get operation completed successfully"
		else:
			#There is no file to GET!
			sublime.message_dialog("Cannot Get file: " + remote_file_path + ". File doesn't exist.")
			return


class get_filesCommand(sublime_plugin.WindowCommand):
	def run(self, files):
		#Run this function for the file passed
		for f in files:
			self.window.run_command("get_file", f)

	def is_visible(self, files):
		return len(files) > 0

class get_dirsCommand(sublime_plugin.WindowCommand):
	def run(self, dirs):
		settings = sublime.load_settings("Remote Directory.sublime-settings")

		local_path_mask = sublime.active_window().active_view().settings().get("local_path_mask", settings.get("local_path_mask", ""))
		remote_path_mask = sublime.active_window().active_view().settings().get("remote_path_mask", settings.get("remote_path_mask", ""))

		for d in dirs:
			local_file_path = d
			local_file_index = local_file_path.find(local_path_mask)

			if local_file_index == -1:
				#sublime.message_dialog("The local_path_mask(path:: " + local_file_path + " mask:: " + local_path_mask + ") is invalid for the current file. GET aborted.")
				return

			local_file_index += len(local_path_mask)
			path = d[local_file_index:]

			for root, dirs, files in os.walk(remote_path_mask + path):
				for f in files:
					#Take the root, and substract the remote_path_mask
					root_file_index = root.find(remote_path_mask)

					root_file_index += len(remote_path_mask)
					path = local_path_mask + root[root_file_index:]

					#Check to see if the directory exists locally. Create it if it doesn't
					if not os.path.isdir(path):
						os.makedirs(path)
						print "Created directory \"" + path + "\""

					print "Getting file \"" + path + "/" + f + "\""
					self.window.run_command("get_file", path + "\\" + f)

	def is_visible(self, dirs):
		return len(dirs) > 0