# Remote Directory

Remote Directory is a Sublime Text 2/3 plugin which allows you to keep a project in two locations at the same time. The general use-case here is when you have a working directory, and another directory where files need to be placed into in order to work (think webroot when developing for the web). Typically this is done through FTP or some other networked system, but when you're working on a personal project or something smaller scale, FTP can be overkill. Particularly if the drive you're developing on is the same machine as your webserver. Another use-case is when you want to keep something stored in Dropbox, but you don't want to actually develop it in your Dropbox folder. It's important to note that Remote Directory only works with files accessible through your local machine; this isn't an FTP client. 

##How it Works

Let's say that you want to keep all your development files organized in a subdirectory of your documents folder, and that you need these files to be copied into your webroot whenever you save them in Sublime. For the purpose of this demonstration, lets say that these are the two directories:

``C:\Users\Steve\Documents\Sweet Program\``

``C:\Railo\webroot\Sweet Program\``

In Remote Directory, the first path is referred to as the **local path**, and the second is referred to as the **remote path** (pretty easy right?). So when you save a file in Sublime, if it is in the local path (or a subdirectory thereof), Remote Directory will attempt to copy the file to the corresponding location in the remote path. Remote Directory will create any subdirectories or files necessary to do this.

What happens if someone (or something) else modifies the file since the last time that you sent it to the remote (put)? Well, without intervention, it would be overwritten, which may or may not be a problem. To deal with this Remote Directory keeps track of the last time that you copied the remote file to your local path (get). If the remote file has been modified since the last time that you did this, then it will refuse to ``put`` the file until you perform the ``get`` operation. This prevents you from overwritting something you might have preferred to keep.

##Installation & Setup

To install Remote Directory, download the zip file and extract it into your Packages folder.

Once Remote Directory is installed, you'll really need to set up settings in each Sublime project you want to use it with. For each project you want to use Remote Directory with, you'll need to add the following settings to your Project. You can change your project specific settings by using ``Project -> Edit Project``.

```

"settings":
{
	"remote_directory":
	{
		"local_mask": "C:\\Users\\Steve\\Documents\\Sweet Program\\",
		"remote_mask": "C:\\Railo\\webroot\\Sweet Program\\",
		"history_file": "sublime_gethistory.txt",
		"exclude_extensions": [".txt", ".dll"],
		"exclude_directories": [".git"],
		"debug": "False"
	}
}

```

The only required settings of those above are the two masks (local_mask and remote_mask). Everything else is included for completeness, but Remote Directory will work without them. Also, note that the settings provided above are purely for demonstration purposes and as such it's strongly recommended that you change your settings to values appropriate to you. But we're all programmers here, I'm sure that you knew that =]

###Settings

* ``local_mask`` - The local path. Make sure to escape all backslashes since this is a JSON string.
* ``remote_mask`` - The remote path. Make sure to escape all backslashes here as well.
* ``history_file`` - The name of the history file, which keeps track of the last time you used the ``get`` command on a remote file. You can change this to whatever you want, but if you change it, make sure you change the names of any generated history files so that Remote Directory knows where to look.
* ``excluded_extensions`` - An array of file extensions to ignore. Remote Directory just looks at the end of a file to see if it contains the extension. You can use this to ignore a specific filename as well, since it really just compares the filename to each of the strings in this array.
* ``excluded_directories`` - An array of paths, or directory names. If the path of the file contains anything in this array, the operation will abort. This means you can specify partial paths or a specific folder name (as in the example above), but it also means that it's pretty easy to accidentally exclude something you're trying not to exclude.
* ``debug`` - Defaults to False. Used to decide whether debug output should be sent to the console. If you're not sure whether something is working properly, you might be able to troubleshoot it using this option. If it's set to False, then nothing will be sent to the console.

Again, only the local_mask and remote_mask are required.


##Usage

Using Remote Directory is fairly simple. The main actions are ``get`` and ``put``.

###Get

You can get the remote version of a local file in one of several ways:
 1. With the local file open in the current buffer, right click and select **Get remote file** from the context menu. This will get the contents of the corresponding remote file and put them in the currently open buffer.
 2. Right click on a file or directory in the side bar and select **Get remote Directory** (or file).
 3. Use the command palette and select **Remote Directory: Get remote file**
 4. Using a keyboard shortcut. By default this is (ctrl+alt+x)
 
Once a file is retrieved using the ``get`` command, you can use the ``put`` command.

###Put

You can write the local version of a file to the corresponding remote directory in one of several ways.: 
 1. With the local file open in the current buffer, right click and select **Put local file** from the context menu.
 2. Use the command pallet and select **Remote Directory: Put local file**
 3. Save the file using any normal means (File->Save, command palette, etc)
 4. Right click on a file or directory in the side bar and select **Put local directory** (or file).


###History files

Remote Directory keeps track of ``gets`` using a file created in the local directory of any file being retrieved. By default, this file is named sublime_gethistory.txt. You should make sure to exclude this file from stuff like git and whatever, but it'll probably be ok if you forget. You can change the name of the history file by modifying your settings (either by project of using the global plugin settings). The history file doesn't need to have an extension.
