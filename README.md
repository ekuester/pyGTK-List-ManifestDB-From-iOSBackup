# pyGTK-List-ManifestDB-From-iOSBackup
Read and extract files from iOS backup made by iTunes ( Python / Linux / Gnome / GTK / pyGTK )

Program for parsing an iOS Backup generated by iTunes for iPad and iPhone</br>
( See what is covered under the hood of iOS )

While working under Fedora Linux I am arriving now from  C++ to Python as the programming language and I am surprised now how concise the language in combination with pyGTK performs.

Since Python is an interpretative language you simply start the program in command line by executing

```
python3 manifestDVview.py
```
In the moment exists no localization (on the TO-DO-list).

The program follows the design of the earlier programs List-ManifestDB-From-iOSBackup written in Swift and GTK-List-ManifestDB-from iOSBackup written in C++ (published in my repository).

I wrote this program to become familiar with the Python language, especially the pyGTK for the GTK-API (which I was using with gtkmm wrapper earlier) and to get a feeling how to display multiple widgets on the screen. Take it as example for handling of windows, boxes, comboboxes, treeviews, textviews and more, but now in pyGTK. The final reason for choosing python was the wonderful module 'plistlib' for decoding binary plists (I found no simple solution for C or C++).

### Background:
The file Manifest.mbdb describes no longer the backup files for iOS. Beginning with iTunes version 12.5 (or so) the main information for the files is stored in a SQLite database Manifest.db (iTunes as of macOS Sierra and higher is using this scheme in any case, BTW just as under Windows 10).

The structure of this database is as follows 
```
$ sqlite3
sqlite> .open Manifest.db
sqlite> .fullschema
CREATE TABLE Files (fileID TEXT PRIMARY KEY, domain TEXT, relativePath TEXT, flags INTEGER, file BLOB);
CREATE INDEX FilesDomainIdx ON Files(domain);
CREATE INDEX FilesRelativePathIdx ON Files(relativePath);
CREATE INDEX FilesFlagsIdx ON Files(flags);
CREATE TABLE Properties (key TEXT PRIMARY KEY, value BLOB);
.quit
```
Access to SQLite under Python proved to be much more easier than with C++ ... [1]]

The same conclusion is valid for reading of BLOBs (binary large objects).

Use the program for extracting of backup'd files which could not be recovered otherwise.

### Usage:
- Click on "Open" left in the toolbar above to open an appropiate data base file. The Backup is structured in so-called domains.
- Down right there is now appearing a button "Export CSV...". Clicking will export the data base structure to an ',' separated CSV file, which can be read in a text editor or calculation program of your choice.
- Normally exist in the same directory two files 'Manifest.plist' and 'Status.plist" which will be displayed by the related Buttons located left and in the middle, otherwise they are invisible.
-  Choosing a domain from the appearing Combobox will display further components of this domain. Double-clicking a row in the table opens a dialog where you can select the place for storing the requested file.
- If you know which domain you are looking for, enter in the entry field of the Combobox a significant segment for the name and press key 'Enter'. The first entry which will match is then selected. So typing in 'CameraRoll' will fetch the CameraRollDomain, where you find your stored images.
- Clicking the "Extract Domain..." button will export the whole domain into a directory of your choice (but makes sense only if files are present, of course). The progress is shown in a dialog window with a progressbar.
- Quit the program with "Quit" or by closing the application window.

### Acknowledgements:
- David Blache for some fundamentals about iOSBackup and his idea to export a CSV file.</br>
<https://www.quora.com/How-do-I-access-and-read-a-file-from-my-iPhone-backup-on-my-PC>
- Marnix Kaart for an excellent python solution (some of his code was very inspirational).</br>
<https://github.com/mx-pycoder/pearback>
- Special thanks go to the people in the developer community at StackOverflow. Without their help and answered questions at <https://stackoverflow.com/> and affiliate sites this work would not be possible.

### Literature
[1] <https://docs.python.org/3/library/sqlite3.html>

### Disclaimer:
Use the program for what purpose you like, but hold in mind, that I will not be responsible for any harm it will cause to your hard- or software. It was your decision to use this piece of software.
