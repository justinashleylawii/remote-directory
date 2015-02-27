# remote-directory

Remote-Directory is a Sublime Text 2 plugin which allows you to save a file in a second location whenever you use the save command. Basically, let's say that you have a directory where you like to write all of your programs, but in this case, the program you're writing happens to be a web application which you need to run from within wwwroot or something. Once set up, remote-directory will, when you save a file to your documents folder (or wherever you keep your code), save the file in the appropriate place in the wwwroot as well. Note that even though it's called remote directory, the file needs to be part of your filesystem. This is not an FTP front-end.

When saving a file to a shared directory, where someone else might modify the file, your work is at risk of being overwritten (obviously if you're not a scrub, then you're using version control (ever heard of git?), and this senario doesn't hold). Remote-directory compensates for this by keeping track of the last time you retrieved a copy of the remote file. If you try and save a file which has been modified since the last time you retrieved it, Sublime will yell at you and refuse to do it.

##Setup

Once you've installed the remote-directory plugin to Sublime, if you want it to actually do anything, you need to tell it where you want files to go. Currently, these settings are on a per-project basis. (I think this also works with the regular settings file if you don't create projects)

Once you have a project opened in Sublime, you can access the project settings by going to Project->Edit Project in the toolbar at the top. Sublime will open your project specific .sublime-project file.

If you're unfamiliar with Sublime's different configuration files, they're essentially JSON files which contain a series of structures, arrays, keys, and values which are interpreted by Sublime and its plugins to change the way it operates. Add the following to your project settings file:

```javascript
"settings":
{
	"local_path_mask":"your local path goes here",
	"remote_path_mask":"your remote path goes here"
}
```

Change "your local path goes here" to values which correspond to your environment.

###Path Masks

First, I have to tell you something which you've probably already noticed if you're reading this: This plugin isn't polished at all. It's not user friendly, and there are some things that really suck about it. I made this for my own use, but figured other people might be able to benefit from it. I will fix some of these things if there's ever a demand for it, but until then just think of it as being in alpha.. or something.

Anyway, path masks are remote-directory's way of deciding what should be moved to the remote directory, and to what remote-directory it should be moved.

####Local Path Mask

A local path mask might look like:
```
C:\\Users\\yourname\\Documents\\program\\yourproject
```

Note the double backspaces are just regular backspaces being escaped, so the actual path is:
```
C:\Users\yourname\Documents\program\yourproject
```

This means that any file you save in 
```
C:\Users\yourname\Documents\program\yourproject
```
or **any of its subdirectories** will be saved using remote-directory.

####Remote Path Mask

Likewise, the remote path mask might look like: 
```
\\\\sharedDrive\\webserver\\wwwroot\\yourproject
```
When you save the file *test.txt* in:
```
C:\Users\yourname\Documents\program\yourproject
```
remote-directory will attempt to save the file:
```
\\\\sharedDrive\\webserver\\wwwroot\\yourproject\\test.txt
```


Additionally, if you save a file in: 
```
C:\\Users\\yourname\\Documents\\program\\yourproject\\subdirectory
```
remote-directory will try to save:
```
\\\\sharedDrive\\webserver\\wwwroot\\yourproject\\subdirectory\\test.txt
```

###Caveats

Currently, remote-directory won't create any folders. So in the above example, "subdirectory" needs to already exist. Otherwise, it does nothing. Also, if the remote file already exists, it will only be overwritten if the remote file has been retrieved more recently than it has been written. More on that in the *Usage* section. If a file is outside of the local path mask, nothing happens. Which is good, so that random files on your computer aren't being replicated elsewhere on your computer unless you set up your masks to allow that.

##Usage

Using remote-directory is fairly simple. The main actions are **GET** and **PUT**.

###Get

You can get the remote version of a local file in one of several ways.  
 1. With the local file open in the current buffer, right click and select **Get remote file** from the context menu. This will get the contents of the corresponding remote file and put them in the currently open buffer.
 2. Right click on a file or directory in the side bar and select **Get remote Directory** (or file).
 3. Use the command pallet and select **Remote Directory: Get remote file**
 4. Using a keyboard shortcut. By default this is (ctrl+alt+x)
 
Once a file is retrieved using the Get command, you can perform a Put.

###Put

You can write the local version of a file to the corresponding remote directory in one of several ways.  
 1. With the local file open in the current buffer, right click and select **Put remote file** from the context menu.
 2. Use the command pallet and select **Remote Directory: Put remote file**
 3. Save the file using any normal means (File->Save, command pallet, etc)
 
If the operation was successful, a message will be printed in the console (ctrl+` on Windows).

###History files

Remote-directory keeps track of gets and puts using a file created in the local directory of any file being retrieved. This file is named sublime_gethistory.txt. You should exclude this file from stuff like git and whatever, but it'll probably be ok if you forget.

You can change the name of the history file by modifying the following line in the *Remote Directory.sublime-settings* file:

```
"history_file_name":"sublime_gethistory.txt"
```

Just change sublime_gethistory.txt to whatever you want. It doesn't need to be a txt file.

##Notes

I've run this plugin on Mac OSX, Windows 8, and Linux (CentOS), and I've used it to write files to Dropbox folders, file shares, and other directories on my computer. That being said, I know there are bugs. There may even be some bad ones. If you find one, create an issue for it and I'll fix it.
