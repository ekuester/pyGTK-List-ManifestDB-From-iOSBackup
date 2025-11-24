#!/usr/bin/env python3
# see https://python-gtk-3-tutorial.readthedocs.io/en/latest/
#  List ManifestDB
#  See what is covered under the hood of IOS
#
#  File: manifestDBview.py
#
#  Program for parsing the Backup files of IOS for iPad and iPhone, generated
#    by iTunes versions higher than 12.5 or so ( older versions are using a
#    different method for a backup ).
#   The main information is stored in a SQLite database named Manifest.db .
#   To access the database from Linux
#   A. Backup was done under MacOS (ignore if you are using APFS):
#   1. mount the device where macOS is installed 
#    $ udisksctl mount --block-device /dev/sda2
#   2. authentificate yourself, then you will see where the device is mounted,
#    for instance: /dev/sda2 at /run/media/kuestere/MacBookPro SSD
#   Standard path then - going out from above - is
#     userdirectory /Users/kuestere/ (depending of registered user),
#     default subdirectory then is Library/Application\ Support/MobileSync/Backup,
#     the SQLite database is found in a subdirectory of that.
#   B. Backup was done under Windows (recommended):
#   1. mount the device where Microsoft Windows (actual Version 11) is installed,
#   2. look for the Users folder,
#   3. the relevant folder consists out of a sequence of numbers
#     situated in .../AppData/Roaming/Apple Computer/MobileSync/Backup
#   4. copy the backup folder over into linux system e.g. into ./Downloads
#     This is IMPORTANT, otherwise Windows refuses reading of the data base.
#
#  Use the program for extracting of stored files which could not be recovered otherwise.
#           Created by Erich Küster first on October 3, 2016
#
#  Access to SQLite under C++ was realized analogous to the first answer given at
#  <http://stackoverflow.com/questions/24102775/accessing-an-sqlite-database-in-swift>
#  The old code (in Swift, now abandoned) was rewritten as of July 25, 2018
#     now in C++ with the GTK+ wrapper gtkmm, last changes January 2021
#       to use plistlib rewritten for GTK3 Python on February 8, 2021
#                  last changes Sun, November 23, 2025
#         Copyright © 2016-2025 Erich Küster. All rights reserved.

import csv, os, queue, re, sqlite3, sys, threading

import gettext
_ = gettext.gettext

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio, GLib, GObject
import plistlib as _plistlib
from datetime import datetime
from inspect import currentframe
from time import sleep

# local modules
import toolbar

svg = """
<svg id="svg154" width="256" height="256" version="1.1" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg" xmlns:cc="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:xlink="http://www.w3.org/1999/xlink">
 <defs id="defs142">
  <linearGradient id="linearGradient868" x1="98" x2="98" y1="98" y2="195.5" gradientTransform="matrix(1.2308 0 0 1.2308 8.8767 8.7226)" gradientUnits="userSpaceOnUse">
   <stop id="stop864" stop-color="#ff0035" offset="0"/>
   <stop id="stop866" stop-color="#fd5" offset="1"/>
  </linearGradient>
  <linearGradient id="linearGradient862" x1="138.69" x2="221.78" y1="167.91" y2="167.91" gradientUnits="userSpaceOnUse" xlink:href="#linearGradient868"/>
  <linearGradient id="linearGradient887" x1="93.205" x2="128.06" y1="140.09" y2="98.375" gradientTransform="translate(-3.0196)" gradientUnits="userSpaceOnUse" xlink:href="#linearGradient868"/>
  <linearGradient id="linearGradient893" x1="105.77" x2="103.04" y1="35.507" y2="16.058" gradientTransform="matrix(.29209 0 0 3.4236 12.98 1.357)" gradientUnits="userSpaceOnUse" xlink:href="#linearGradient868"/>
  <linearGradient id="linearGradient895" x1="149.64" x2="201.03" y1="47.501" y2="108.7" gradientTransform="matrix(.82996 0 0 1.2049 12.98 1.357)" gradientUnits="userSpaceOnUse">
   <stop id="stop121" stop-color="#ffb380" offset="0"/>
   <stop id="stop123" stop-color="#ff2a2a" offset="1"/>
  </linearGradient>
  <filter id="filter854" x="-.072" y="-.072" width="1.144" height="1.144" color-interpolation-filters="sRGB">
   <feGaussianBlur id="feGaussianBlur856" stdDeviation="3.5141602"/>
  </filter>
 </defs>
 <rect id="rect1206" x="8.1453" y="8.1453" width="240" height="240" rx="32" ry="32" fill="#fff" fill-opacity=".93891" stroke="#e9e5e5" stroke-width="3.7795"/>
 <path id="path146" d="m45.862 138.9h-4.5633v-60.979h4.5633zm-2.3466-75.927c-1.9244 0-3.5158-1.5265-3.5158-3.4509 0-1.9812 1.5833-3.5158 3.5158-3.5158 1.9812 0 3.5564 1.5265 3.5564 3.5158 0 1.9244-1.5752 3.4509-3.5564 3.4509z" fill="url(#linearGradient893)" fill-rule="evenodd"/>
 <path id="path148" d="m90.185 140.09c-22.313 0-36.409-16.248-36.409-42.076 0-25.699 14.161-42.011 36.409-42.011s36.401 16.313 36.401 42.011c0 25.829-14.096 42.076-36.401 42.076zm0-79.89c-19.422 0-31.821 14.664-31.821 37.813 0 23.166 12.456 37.887 31.821 37.887 19.422 0 31.821-14.721 31.821-37.887 0-23.157-12.399-37.813-31.821-37.813z" fill="url(#linearGradient887)" fill-rule="evenodd"/>
 <path id="path150" d="m159.08 140.09c-16.751 0-28.76-9.4595-29.442-22.987h4.474c0.68206 11.092 11.1 18.854 25.309 18.854 13.868 0 23.547-7.8761 23.547-18.513 0-8.5582-5.7731-13.479-19.471-16.93l-9.6787-2.3791c-15.111-3.8569-21.972-9.971-21.972-20.21 0-12.74 11.895-21.915 26.787-21.915 15.395 0 26.892 9.0616 27.404 21.063h-4.474c-0.62522-9.7924-10.19-16.93-23.044-16.93-12.293 0-22.086 7.3646-22.086 17.668 0 8.1603 6.0005 12.854 19.13 16.134l9.1184 2.3222c15.793 3.9056 22.873 9.971 22.873 20.835 0 13.527-11.376 22.987-28.476 22.987z" fill="url(#linearGradient895)" fill-rule="evenodd"/>
 <text id="text1188" x="-110.63005" y="153.78233" fill="#000000" font-family="sans-serif" font-size="40px" style="line-height:1.25" xml:space="preserve"><tspan id="tspan1186" x="-110.63005" y="153.78233"/></text>
 <text id="text1192" x="87.968163" y="180.4267" fill="url(#linearGradient862)" font-family="sans-serif" font-size="42.667px" style="line-height:1.25;mix-blend-mode:normal" xml:space="preserve"><tspan id="tspan1190" x="87.968163" y="180.4267" fill="url(#linearGradient862)" font-family="'Noto Sans'" font-size="42.667px">Backup</tspan></text>
 <path id="path849" transform="matrix(2 0 0 2 .14531 .14531)" d="m117.14 6.8613c1.8003 2.5889 2.8613 5.7328 2.8613 9.1387v88c0 8.864-7.136 16-16 16h-88c-3.4059 0-6.5498-1.061-9.1387-2.8613 2.8851 4.1488 7.6806 6.8613 13.139 6.8613h88c8.864 0 16-7.136 16-16v-88c0-5.4581-2.7126-10.254-6.8613-13.139z" filter="url(#filter854)" opacity=".36"/>
</svg>"""

###########
#   CSS   #
###########
screen = Gdk.Screen.get_default()
provider = Gtk.CssProvider()

style_context = Gtk.StyleContext()
style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

# for color schemes see <https://graphviz.org/doc/info/colors.html>
# use prefix `b` or `.encode()` to create `bytes`
css = b"""
#nice-entry {color: yellow; background: darkolivegreen; font-weight: bold} 
#red-button {background: #fdd}
"""

provider.load_from_data(css)

###########
# classes #
###########
class InfoDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, transient_for=parent, flags=0)
        self.move(272, 64)
        self.add_buttons(
            'Copy', 100, Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE
        )
        self.set_default_size(160, 96)
        self.set_default_response(100)
        self.set_border_width(8)

        label = parent.dialog_label
        label.set_margin_top(32)
        label.set_margin_bottom(32)
        box = self.get_content_area()
        box.add(label)
        self.show_all()

class ProgressThread(threading.Thread):
    def __init__(self, queue, grand_parent):
        threading.Thread.__init__(self)
        self._extract_path = grand_parent.extract_path
        self._files = grand_parent.files
        self._queue = queue

    def run(self):
        file_count = 0
        subtotal = 0
        for file in self._files:
            file_url = file['fileURL']
            target_url = os.path.join(self._extract_path, file['relativePath'])
            target_dirs = os.path.dirname(target_url)
            os.makedirs(target_dirs, exist_ok=True, mode=0o750)
            try:
                with open(file_url, 'rb') as fr, open(target_url, 'wb') as fw:
                    while True:
                        chunk = fr.read(1024)
                        if chunk: 
                            fw.write(chunk)
                        else:
                            break
            except EnvironmentError:
                self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                    _('An error occurred while copying, good luck!'))
            finally:
                file_count += 1
                subtotal += file['fileSize']
                self._queue.put(subtotal)
        self.window.context_id = self.window.status_bar.push(self.window.context_id,\
            _('{} files extracted to: {}').format(file_count, self._extract_path))


class ProgressbarDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, title=_("Filetransfer"), transient_for=parent.window, flags=0)  
        self.move(272, 64)
        self.set_modal(True)
        self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        self.set_default_size(216, 64)
        self.set_border_width(8)
        self.connect("response", self._on_response)
        label = Gtk.Label(label=_("Copying Files ..."))
        self.progressbar = Gtk.ProgressBar(show_text=True)
        box = self.get_content_area()
        box.add(label)
        box.add(self.progressbar)
        self.show_all()
        # total number of bytes to copy
        self._total = parent.total
        # queue to share data between threads
        self._queue = queue.Queue()
        # install timer event to check the queue every interval for new data from the thread
        GLib.timeout_add(interval=20, function=self._on_timer)
        # start the thread
        self._thread = ProgressThread(self._queue, parent)
        self._thread.daemon = True
        self._thread.start()

    def _on_timer(self):
        # if the thread is dead and no more data available...
        if not self._thread.is_alive() and self._queue.empty():
            # ...end the timer
            return False
        # if data available
        while not self._queue.empty():
            # read data from the thread
            subtotal = self._queue.get()
            # update the progressbar
            self.progressbar.set_fraction(subtotal / self._total)
        # keep the timer alive
        return True

    def _on_response(self, dialog, response_id):
        dialog.destroy()

class Window(Gtk.ApplicationWindow):
    def __init__(self, app):
        super(Window, self).__init__(title=_('Gtk+: iOS Backup - Read Manifest.db'),\
    application=app)
        self.set_border_width(8)
        self.set_default_size(800, 600);
        loader = GdkPixbuf.PixbufLoader()
        loader.write(svg.encode())
        loader.close()
        pixbuf = loader.get_pixbuf()
        self.set_icon(pixbuf)
        # vertical box to hold the widgets
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # a toolbar created in the method create_toolbar (see below)
        _toolbar = toolbar.create(self)
        # add the toolbar to the vertical box
        self.vbox.pack_start(_toolbar, False, True, 0)
        label = Gtk.Label()
        label.set_markup("<span face=\"mono\" weight=\"bold\">iOSBackup </span>")
        self.label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.label_box.pack_start(label, True, True, 0)
        self.vbox.pack_start(self.label_box, True, True, 0)

        # some needed stuff
        self.first_run = True
        settings = Gtk.Settings.get_default()
        theme_name = settings.get_property("gtk-theme-name")
        self.is_dark = "dark" in theme_name.lower()
        self.backup_path = str()
        # records of 'naked' domains
        self.naked_domains = []
        self.domain_items = []
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.dialog_label = Gtk.Label()
        self.dialog_label.set_justify(Gtk.Justification.LEFT)

        # create combobox with entry
        listmodel = Gtk.ListStore(str, int)
        self.combo = Gtk.ComboBox.new_with_model_and_entry(model=listmodel)
        # cellrenderers to render the data
        renderer_text = Gtk.CellRendererText()
        self.combo.pack_start(renderer_text, True)
        self.combo.add_attribute(renderer_text, "text", 1)
        # active row at the beginning is undefined
        self.combo.set_active(-1)
        self.combo.connect("changed", app.on_combo_changed)
        self.combo.set_entry_text_column(0)
        entry = self.combo.get_child()
        entry.set_name('nice-entry')
        placeholder = _("Please select domain to display")
        entry.set_text(placeholder)
        # handles Enter pressed
        entry.connect("activate", app.on_entry_activate)
        # button extract domain
        domain_button = Gtk.Button.new_with_label(_("Extract Domain..."))
        domain_button.set_tooltip_text(_("Extract domain content"))
        # label is shown
        domain_button.show()
        # set the name of the action associated with the button.
        domain_button.connect("clicked", app.on_extract_domain_clicked)
        # combination of combobox and button
        self.domain_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.domain_box.pack_start(self.combo, True, True, 0)
        self.domain_box.pack_end(domain_button, False, True, 0)
        # create scrolled_window for treeview under the combobox
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_size_request(-1, 384)
        self.scrolled_window.set_border_width(0)
        # options for the scrollbars (ALWAYS, AUTOMATIC, NEVER)
        self.scrolled_window.set_policy(\
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        # model creation for the treeview
        treemodel = Gtk.ListStore( str, str, 'glong')
        # create TreeView
        self.treeview = Gtk.TreeView(model=treemodel)
        treeview_columns = ['fileID', 'relativePath', 'flags']
        for col_num, name in enumerate(treeview_columns):
            # align text in column cells of row (0.0 left, 0.5 center, 1.0 right)
            rendererText = Gtk.CellRendererText(xalign=0.0, editable=False)
            column = Gtk.TreeViewColumn(name ,rendererText, text=col_num)
            column.set_cell_data_func(rendererText, self.celldatafunction, func_data=col_num)
            # center the column titles in first row
            column.set_alignment(0.5)
            # make all the column reorderable, resizable and sortable
            column.set_sort_column_id(col_num)
            column.set_reorderable(True)
            column.set_resizable(True)
            self.treeview.append_column(column)
        # Connect signal handler
        self.treeview.connect("row_activated", app.on_row_activated)
        '''
        # create the Text Buffer
        text_buffer = Gtk.TextBuffer.new()
        text_view = Gtk.TextView()
        text_view.set_buffer(text_buffer);
        # add the TextView, inside a ScrolledWindow under the tableview
        text_window = Gtk.ScrolledWindow()
        text_window.set_size_request(-1, 60)
        text_window.add(text_view);
        # only show the scrollbars when they are necessary:
        text_window.set_policy(\
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
'''
        self.status_frame = Gtk.Frame()
        self.status_bar = Gtk.Statusbar()
        self.status_frame.add(self.status_bar)
        self.vbox.pack_end(self.status_frame, False, True, 0)
        self.context_id = self.status_bar.push(0, _("Choose a Database, click Open"))
        self.add(self.vbox)

    def celldatafunction(self, column, cell, model, iter, func_data):
        # column is provided, but not used
        col_num = func_data
        value = model.get(iter, col_num)[0]
        if type(value) is int:
            cell.set_property('text', f'{value:>8d}')
        path = model.get_path(iter)
        row = path[0]
        # background color depends on theme
        b_colors = []
        if self.is_dark:
            b_colors = ['darkolivegreen', 'black']
        else:
            b_colors = ['darkolivegreen', 'white']
        cell.set_property('cell-background', b_colors[row % 2])

class Application(Gtk.Application):
    def __init__(self):
        super(Application, self).__init__()

    def do_activate(self):
        self.window = Window(self)
        self.window.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        action = Gio.SimpleAction.new("open", None)
        action.connect("activate", self.on_open)
        self.add_action(action)
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

    def add_filters(self, dialog):
        filter_db = Gtk.FileFilter()
        filter_db.set_name(_("Database files"))
        filter_db.add_mime_type("application/vnd.sqlite3")
        dialog.add_filter(filter_db)

        filter_text = Gtk.FileFilter()
        filter_text.set_name(_("Text files"))
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name(_("Any files"))
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def choose_database_file(self):
        dialog = Gtk.FileChooserDialog(
            title=_("Select Manifest.db file"), parent=self.window, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        self.add_filters(dialog)
        response = dialog.run()
        filename = None
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
        dialog.destroy()
        return filename

    def read_binary_plist(self, file):
        try:
            with open(file, 'rb') as f:
                s = _plistlib.load(f)
            keys = sorted(s.keys())
            vals = [s[k] for k in keys]
            return dict(zip(keys, vals))
        except EnvironmentError:
            return None
 
    def on_open(self, action, parameter):
        if (self.window.first_run is False):
            self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                _("Go on to open a new Database"))
        backup_url = self.choose_database_file()
        if (backup_url is None):
            self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                _("No Database chosen, try again"))
            return
        self.backup_path = os.path.dirname(backup_url)
        manifest_file = os.path.join(self.backup_path,'Manifest.plist')
        self.manifest = self.read_binary_plist(manifest_file)
        status_file = os.path.join(self.backup_path,'Status.plist')
        self.status = self.read_binary_plist(status_file)

        try:
            sqliteConnection = sqlite3.connect(backup_url)
            cursor = sqliteConnection.cursor()
            self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                _("Database created and successfully connected to SQLite"))
            query = "SELECT * FROM Files"
            cursor.execute(query)
            self.records = cursor.fetchall()
            # order column names into first tuple of the list
            self.names = list(zip(*cursor.description))
            # truncate list to first tuple
            del self.names[1:]
            cursor.close()
        except sqlite3.Error as error:
            self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                _("Error while connecting to sqlite"))
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                    _("The SQLite connection is closed after reading"))

        listmodel = self.window.combo.get_model()
        treemodel = self.window.treeview.get_model()
        if (len(self.window.naked_domains)):
            del self.window.naked_domains[:]
            # clear entry and models
            self.window.combo.set_active(-1)
            entry = self.window.combo.get_child()
            placeholder = _("Please select domain to display")
            entry.set_text(placeholder)
            listmodel.clear()
            treemodel.clear()
        # filter out "naked" domains where relativePath is empty
        for record in self.records:
            path = record[2]
            if (not path):
                self.window.naked_domains.append(record[1])
        # sort in ascending order
        self.window.naked_domains.sort()
        # fill combobox listmodel
        index = 0
        for naked_domain in self.window.naked_domains:
            index += 1
            listmodel.append([naked_domain, index])
        self.window.context_id = self.window.status_bar.push(self.window.context_id,\
            _('Combobox filled with {} domain names, please select one').format(index))
        self.window.remove(self.window.vbox)
        if (self.window.first_run):
            # prepare scrolled window
            self.window.scrolled_window.add(self.window.treeview)
            self.window.scrolled_window.show()
            # add new widgets and reorder
            self.window.vbox.remove(self.window.label_box)
            # add horizontal combobox
            self.window.vbox.pack_start(self.window.domain_box, False, False, 0);
            self.window.vbox.pack_start(self.window.scrolled_window, False, True, 0)
            self.window.vbox.pack_start(self.window.label_box, True, True, 0)
            # generate horizontal box at bottom for manifest, status, export
            self.window.bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            self.window.bottom_box.set_border_width(0)
            # prepare button for Manifest.plist
            self.window.manifest_button = Gtk.Button.new_with_label("Manifest.plist")
            self.window.manifest_button.connect("clicked", self.on_manifest_show_clicked, True)
            self.window.bottom_box.pack_start(self.window.manifest_button, False, True, 0)
            # prepare button for Status.plist
            self.window.status_button = Gtk.Button.new_with_label("Status.plist")
            self.window.status_button.connect("clicked", self.on_status_show_clicked, True)
            self.window.bottom_box.pack_start(self.window.status_button, True, False, 0)
            export_button = Gtk.Button.new_with_label(_("Export CSV..."))
            export_button.connect("clicked", self.on_export_csv)
            self.window.bottom_box.pack_end(export_button, False, True, 0)
            self.window.bottom_box.pack_end(export_button, True, True, 0)
            self.window.vbox.pack_start(self.window.bottom_box, False, True, 0)
            self.window.first_run = False
        self.window.manifest_button.set_sensitive(self.manifest is not None)
        self.window.status_button.set_sensitive(self.status is not None)
        self.window.add(self.window.vbox)
        self.window.show_all()

    def on_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            domain, row_id = model[tree_iter][:2]
            treemodel = self.window.treeview.get_model()
            # delete data of an earlier run
            if (len(self.window.domain_items) > 0):
                del self.window.domain_items[:]
                # make place for new table rows
                treemodel.clear()
            if (row_id > 0):
                # remove vbox from main window
                self.window.remove(self.window.vbox)
                self.window.vbox.remove(self.window.bottom_box)
                self.window.vbox.remove(self.window.label_box)
                self.window.vbox.remove(self.window.scrolled_window)
                ''' self.window.vbox.remove(self.window.text_window) '''
                # filter out file info of the chosen domain
                indices = [0, 2, 3, 4]
                for record in self.records:
                    if (record[1] == domain):
                        selected_items = [record[index] for index in indices]
                        self.window.domain_items.append(selected_items)
                        # do not append file BLOB
                        treemodel.append(selected_items[0:3])
                self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                    _('Chosen domain: {}').format(domain))
                self.window.vbox.pack_start(self.window.scrolled_window, False, True, 0)
                ''' self.vbox.pack_end(self.text_window) '''
                self.window.vbox.pack_start(self.window.label_box, True, True, 0)
                self.window.vbox.pack_end(self.window.bottom_box, False, True, 0)
                self.window.add(self.window.vbox)
                self.window.show_all()
        else:
            entry = combo.get_child()
            # but ignore any input (Enter is treated by signal 'activate' (see below)

    def on_row_activated(self, treeview, path, column):
        model = self.window.treeview.get_model()
        tree_iter = model.get_iter(path)
        row = path[0]
        if tree_iter:
            file_id = model.get_value(tree_iter, 0)
            relative_path = model.get_value(tree_iter, 1)
            target = os.path.basename(relative_path)
            # flags 1 = RegularFile, 2 = Directory, 3 = Symlink
            flags = model.get_value(tree_iter, 2)
            # first have a look at the file BLOB
            domain_item = self.window.domain_items[row]
            file_blob = domain_item[3]
            properties = _plistlib.loads(file_blob)
            buffer = []
            buffer.append(f'<span face="mono" underline="double">{target}\n</span>')
            time_stamps = ("Birth", "LastModified", "LastStatusChange")
            for key in properties:
                if key == '$objects':
                    objects = properties[key]
                    for bodies in objects:
                        if type(bodies) is str:
                            buffer.append(f'<span face="mono">{bodies: <25}</span>')
                        else:
                            # object is dict
                            for body in bodies:
                                if body in time_stamps:
                                    val = datetime.fromtimestamp(bodies[body])
                                else:
                                    val = str(bodies[body])
                                buffer.append(f'<span face="mono">{body: <25} {val} </span>')
                else:
                    val = properties[key]
                    buffer.append(f'<span face="mono">{key: <25} {val} </span>')
            self.show_info_dialog(buffer)
            # only if flags == 1 there is a file to copy
            if flags == 1:
                # get first two characters of file ID
                file_hash = file_id[0:2]
                file_url = os.path.join(self.backup_path, file_hash, file_id)
                self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                    _("URL for backup'd file: {}").format(file_url))
                target_path = self.choose_folder_for_saving(\
                    _("Please choose a folder to copy file in"))
                if (target_path is None):
                    self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                        _("No path for target file given, try again"))
                    return
                target_url = os.path.join(target_path,target)
                try:
                    with open(file_url, 'rb') as fr, open(target_url, 'wb') as fw:
                        while True:
                            chunk = fr.read(1024)
                            if chunk: 
                                fw.write(chunk)
                            else:
                                break
                except EnvironmentError:
                    self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                        _('An error occurred while copying, good luck!'))
                finally:
                    self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                        _('Copying to {} complete, no errors').format(target_url))
            else:
                self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                    _('Saving rejected (wrong file type)'))

    def on_entry_activate(self, entry):
        # on 'Enter' look for first row with domain containing the actual entry text
        self.window.context_id = self.window.status_bar.push(self.window.context_id,\
            _("no match found for entry"))
        search_term = entry.get_text()
        model = self.window.combo.get_model()
        first_match = 0
        column = 0
        for row in model:
            naked_domain = row[0]
            row_id = row[1]
            if search_term in naked_domain:
                # we do have a match
                self.window.combo.set_active(row_id-1)
                entry.set_text(naked_domain)
                self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                    _('first match for entry is {} at row {}').format(naked_domain, row_id))
                break

    def show_info_dialog(self, buffer):
        lines = tuple(buffer)
        report = "\n"
        dialog = InfoDialog(self.window)
        dialog.set_title(_("File Info Dialog"))
        markup = report.join(lines)
        self.window.dialog_label.set_markup(markup)
        response = dialog.run()
        dialog.destroy()
        # convert markup back to normal text
        if response == 100:
            # copy to clipboard
            text = re.sub('<[^<]+?>', '', markup)
            self.window.clipboard.set_text(text, -1)
            self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                _("File Info copied to Clipboard, use Strg-V to retrieve."))

    def on_manifest_show_clicked(self, button, *header):
        buffer = []
        if header[0] is True:
            buffer.append('<span face="mono" underline="double">Manifest.plist\n</span>')
        excludes = ("Applications", "BackupKeyBag", "Lockdown")
        for key in self.manifest:
            val = self.manifest[key]
            if key in excludes:
                if key == "Lockdown":
                    buffer.append(f'<span face="mono">{key: <25} partially skipped </span>')
                    for subname, subval in val.items():
                        if isinstance(subval, dict):
                            # skip the nested dicts
                            continue
                        buffer.append(f'<span face="mono">{subname: <25} {subval} </span>')
                else:
                    buffer.append(f'<span face="mono">{key: <25} skipped </span>')
                continue
            buffer.append(f'<span face="mono">{key: <25} {val} </span>')
        self.show_info_dialog(buffer)

    def on_status_show_clicked(self, button, *header):
        buffer = []
        if header[0] is True:
            buffer.append('<span face="mono" underline="double">Status.plist\n</span>')
        for key in self.status:
            val = self.status[key]
            buffer.append(f'<span face="mono">{key: <25} {val} </span>')
        self.show_info_dialog(buffer)

    def choose_folder_for_saving(self, dialog_title):
        dialog = Gtk.FileChooserDialog(
            title=dialog_title,
            parent=self.window,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)
        # set default selection
        folder = None
        response = dialog.run()
        dialog.hide()
        if response == Gtk.ResponseType.OK:
            folder = dialog.get_filename()
        dialog.destroy()
        return folder

    def on_export_csv(self, widget):
        # export data records into .csv file
        export_path = self.choose_folder_for_saving(_("Please choose a folder for exporting Manifest.csv"))
        if (export_path is None):
            self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                _("No path for CSV file given, try again"))
            return
        export_url = os.path.join(export_path,'Manifest.csv')
        with open(export_url, 'w') as file:
            csv_writer = csv.writer(file, lineterminator='\n')
            for name in self.names:
                csv_writer.writerow(name)
            for record in self.records:
                csv_writer.writerow(record)
            self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                _('Manifest.csv stored in folder {}').format(export_path))

    def on_extract_domain_clicked(self, button):
        model = self.window.treeview.get_model()
        if len(model) == 0:
            self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                _('Select domain first (no rows in model)'))
            return
        self.extract_path = self.choose_folder_for_saving(_("Please choose a folder for extracting files"))
        if (self.extract_path is None):
            self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                _('No path for extracting files given, try again'))
            return
        elif len(os.listdir(self.extract_path)) != 0:
            self.window.context_id = self.window.status_bar.push(self.window.context_id,\
                _('Output directory is not empty!'))
            return
        # now we have a valid extract path
        self.window.context_id = self.window.status_bar.push(self.window.context_id,\
            _('Path to extract files: {}').format(self.extract_path))
        while Gtk.events_pending ():
            Gtk.main_iteration ()
        self.files = list()
        names = ['fileID', 'relativePath', 'flags']
        self.total = 0
        for row in model:
            columns = dict()
            for index, column in enumerate(row):
                columns[names[index]] = column
            if columns['flags'] != 1:
                continue
            else:
                # we have a regular file, add file_URL and file_size
                file_id = columns['fileID']
                # get first two characters of file ID
                file_hash = file_id[0:2]
                file_url = os.path.join(self.backup_path, file_hash, file_id)
                columns['fileURL'] = file_url
                file_size = os.path.getsize(file_url)
                self.total += file_size
                columns['fileSize'] = file_size
                self.files.append(columns)
        if self.total > 0:
            # generate progressbar dialog
            progressbar_dialog = ProgressbarDialog(self)
        else:
            self.window.context_id = self.window.status_bar.push(self.window.context_id,\
               _('Nothing extracted (no regular files in domain)'))

    def on_quit(self, action, parameter):
        self.window.destroy()

    def on_about(self, action, parameter):
        about = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file("about.xpm"));
        about.set_program_name("Gtk+: iOS Backup - Read Manifest.db")
        about.set_size_request(480, -1)
        about.set_version("Version 1.1.14")
        about.set_authors(_("Erich Küster, Krefeld/Germany\n"))
        about.set_copyright("Copyright © 2018-2025 Erich Küster. All rights reserved.")
        with open("COMMENTS","r") as f:
            comments = f.read()
        about.set_comments(comments)
        with open("LICENSE","r") as f:
            license = f.read()
        about.set_license(license)
        about.set_website("http://www.gtkmm.org");
        about.set_website_label("gtkmm Website - C++ Interfaces for GTK+ and GNOME")
        about.set_authors([_("Erich Küster, Krefeld/Germany")]);
        response = about.run()
        if response != Gtk.ResponseType.DELETE_EVENT:
            print(_("Unknown button was clicked"))
        about.destroy()

# available translations
de = gettext.translation('ManifestDBView', localedir='locale', languages=['de'])
de.install()
# define _ shortcut for translations
_ = de.gettext # German
app = Application()
exit = app.run(sys.argv)
sys.exit(exit)

