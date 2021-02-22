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
#   1. mount the device where macOS is installed
#    $ udisksctl mount --block-device /dev/sda2
#   2. authentificate yourself, then you will see where the device is mounted,
#    for instance: /dev/sda2 at /run/media/kuestere/MacBookPro SSD
#   Standard path then - going out from above - is
#     userdirectory /Usxtra window many texters/kuestere/ (depending of registered user),
#     default subdirectory then is Library/Application\ Support/MobileSync/Backup,
#     the SQLite database is found in a subdirectory of that.

#  Use the program for extracting of stored files which could not be recovered otherwise.
#           Created by Erich Küster first on October 3, 2016

#  Access to SQLite under C++ was realized analogous to the first answer given at
#  <http://stackoverflow.com/questions/24102775/accessing-an-sqlite-database-in-swift>
#  The old code (in Swift, now abandoned) was rewritten as of July 25, 2018
#     now in C++ with the GTK+ wrapper gtkmm, last changes January 2021
#       to use plistlib rewritten for GTK3 Python on February 8, 2021
#         Copyright © 2016-2021 Erich Küster. All rights reserved.

import csv, os, re, sqlite3, sys
import gettext
_ = gettext.gettext

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio
import plistlib as _plistlib
from datetime import datetime
from inspect import currentframe

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

##############################
# use f-strings with gettext #
##############################
def  f(s):
    frame = currentframe().f_back
    return eval(f"f'{s}'", frame.f_locals, frame.f_globals)

###########
# classes #
###########
class InfoDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, transient_for=parent, flags=0)
        self.move(272, 64)
        self.add_buttons(
            'Copy', 100, Gtk.STOCK_CLOSE, Gtk.ResponseType.OK
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

class ManifestDBWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Gtk+: iOS Backup - Read Manifest.db")

        self.set_border_width(8)
        self.set_default_size(1024, 768);
        loader = GdkPixbuf.PixbufLoader()
        loader.write(svg.encode())
        loader.close()
        pixbuf = loader.get_pixbuf()
        self.set_icon(pixbuf)

        # vertical box to hold the widgets
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
       
        # a toolbar created in the method create_toolbar (see below)
        toolbar = self.create_toolbar()
        # with extra horizontal space
        toolbar.set_hexpand(True)
        # show the toolbar
        toolbar.show()

        # add the toolbar to the vertical box
        self.vbox.pack_start(toolbar, False, True, 0)

        label = Gtk.Label(label="iOSBackup")
        self.label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.label_box.pack_start(label, True, True, 0)
        self.vbox.pack_start(self.label_box, True, True, 0)

        # some needed stuff
        self.first_run = True
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
        self.combo.connect("changed", self.on_combo_changed)
        self.combo.set_entry_text_column(0)
        combo_entry = self.combo.get_child()
        # handles Enter pressed
        combo_entry.connect("activate", self.on_entry_activate)
        combo_entry.set_text(_("Please select domain to display"))
        # button extract domain
        domain_button = Gtk.Button.new_with_label(_("Extract Domain..."))
        domain_button.set_tooltip_text(_("Extract domain content"))
        # label is shown
        domain_button.show()
        # set the name of the action associated with the button.
        domain_button.connect("clicked", self.on_extract_domain_clicked)
        # combination of combobox and button
        self.domain_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.domain_box.pack_start(self.combo, True, True, 0)
        self.domain_box.pack_end(domain_button, False, True, 0)
        # create scrolled_window for treeview under the combobox
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_size_request(-1, 384)
        self.scrolled_window.set_border_width(0)
        # there is always the scrollbar (otherwise: ALWAYS NEVER)
        self.scrolled_window.set_policy(\
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        # model creation for the treeview
        treemodel = Gtk.ListStore( str, str, 'glong')
        # create TreeView
        self.treeview = Gtk.TreeView(model=treemodel)
        # treeview column headers
        rendererText = Gtk.CellRendererText()
        treeview_cols = ['fileID', 'relativePath', 'flags']
        for num, name in enumerate(treeview_cols):
            column_name = Gtk.TreeViewColumn(name ,rendererText, text=num)
            self.treeview.append_column(column_name)
        # make all the columns reorderable and resizable
        # this is not necessary, but it's nice to show the feature
        for column in self.treeview.get_columns():
            column.set_reorderable(True)
            column.set_resizable(True)
            column.set_alignment(0.7)
        # Connect signal handler
        self.treeview.connect("row_activated", self.on_row_activated)
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
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC) '''

        self.status_frame = Gtk.Frame()
        self.status_bar = Gtk.Statusbar()
        self.status_frame.add(self.status_bar)
        self.vbox.pack_end(self.status_frame, False, True, 0)
        self.context_id = self.status_bar.push(0, _("Choose a Database, click Open"))

        self.add(self.vbox)
        self.show_all()

    # a method to create the toolbar
    def create_toolbar(self):
        # a toolbar
        toolbar = Gtk.Toolbar()
        # which is the primary toolbar of the application
        toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        # toolbar.set_toolbar_style(Gtk.TOOLBAR_BOTH);
        # create a button for the "open" action, with a stock image
        openIcon = Gtk.Image.new_from_icon_name("document-open", Gtk.IconSize.LARGE_TOOLBAR)
        open_button = Gtk.ToolButton.new(openIcon, _("Open"))
        open_button.set_tooltip_text(_("Open data base"))
        # label is shown
        open_button.set_is_important(True)
        toolbar.insert(open_button, 1)
        open_button.show()
        # set the name of the action associated with the button.
        open_button.connect("clicked", self.on_open_clicked)

        # create a button for the "quit" action, with a stock image
        quitIcon = Gtk.Image.new_from_icon_name("application-exit", Gtk.IconSize.LARGE_TOOLBAR)
        quit_button = Gtk.ToolButton.new(quitIcon, _("Quit"))
        quit_button.set_tooltip_text(_("Exit program"))
        # label is shown
        quit_button.set_is_important(True)
        toolbar.insert(quit_button, 2)
        quit_button.show()
        # set the name of the action associated with the button.
        quit_button.connect("clicked", self.on_quit_clicked)

        # create horizontal space
        toolitem_space = Gtk.SeparatorToolItem()
        toolitem_space.set_expand(True)
        toolbar.insert(toolitem_space, 3)

        # create a button for the "about" action, with a stock image
        aboutIcon = Gtk.Image.new_from_icon_name("help-about", Gtk.IconSize.LARGE_TOOLBAR)
        about_button = Gtk.ToolButton.new(aboutIcon, _("About"))
        about_button.set_tooltip_text(_("About program"))
        # label is shown
        about_button.set_is_important(True)
        toolbar.insert(about_button, 4)
        about_button.show()
        # set the name of the action associated with the button.
        #about_button.set_action_name("app.about")
        about_button.connect("clicked", self.on_about_clicked)
        # return the complete toolbar
        return toolbar

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
            title=_("Select Manifest.db file"), parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            filename = None
        dialog.destroy()
        return filename

    def read_binary_plist(self, file):
        try:
            with open(file, 'rb') as f:
                s = _plistlib.load(f)
            keys = sorted(s.keys())
            vals = [s[k] for k in keys]
            xml = dict(zip(keys, vals))
        except EnvironmentError:
            xml = None
        finally:
            return xml

    def on_open_clicked(self, open_button):
        if (self.first_run is False):
            self.context_id = self.status_bar.push(self.context_id,\
                _("Go on to open a new Database"))
        backup_url = self.choose_database_file()
        if (backup_url is None):
            self.context_id = self.status_bar.push(self.context_id,\
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
            self.context_id = self.status_bar.push(self.context_id,\
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
            self.context_id = self.status_bar.push(self.context_id,\
                _("Error while connecting to sqlite"))
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                self.context_id = self.status_bar.push(self.context_id,\
                    _("The SQLite connection is closed after reading"))

        listmodel = self.combo.get_model()
        treemodel = self.treeview.get_model()
        if (len(self.naked_domains)):
            del self.naked_domains[:]
            # clear entry and models
            self.combo.set_active(-1)
            entry = self.combo.get_child()
            entry.set_text(_("Please select domain to display"))
            listmodel.clear()
            treemodel.clear()
        # filter out "naked" domains where relativePath is empty
        for record in self.records:
            path = record[2]
            if (not path):
                self.naked_domains.append(record[1])
        # sort in ascending order
        self.naked_domains.sort()
        # fill combobox listmodel
        index = 0
        for naked_domain in self.naked_domains:
            index += 1
            listmodel.append([naked_domain, index])
        self.context_id = self.status_bar.push(self.context_id,\
            f(_('Combobox filled with {index} domain names, please select one')))

        self.remove(self.vbox)

        if (self.first_run):
            # prepare scrolled window
            self.scrolled_window.add(self.treeview)
            self.scrolled_window.show()
            # add new widgets and reorder
            self.vbox.remove(self.label_box)
            # add horizontal combobox
            self.vbox.pack_start(self.domain_box, False, False, 0);
            self.vbox.pack_start(self.scrolled_window, False, True, 0)
            self.vbox.pack_start(self.label_box, True, True, 0)
            # generate horizontal box at bottom for manifest, status, export
            self.bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            if (self.manifest is not None):
                manifest_button = Gtk.Button.new_with_label("Manifest.plist")
                manifest_button.connect("clicked", self.on_manifest_show_clicked, True)
                manifest_button.show()
                self.bottom_box.pack_start(manifest_button, False, True, 0)
                
            if (self.status is not None):
                status_button = Gtk.Button.new_with_label("Status.plist")
                status_button.connect("clicked", self.on_status_show_clicked, True)
                status_button.show()
                self.bottom_box.pack_start(status_button, True, False, 0)
            export_button = Gtk.Button.new_with_label(_("Export CSV..."))
            export_button.connect("clicked", self.on_export_csv_clicked)
            export_button.show()
            self.bottom_box.pack_end(export_button, False, True, 0)
            self.bottom_box.set_border_width(0)
            self.bottom_box.pack_end(export_button, True, True, 0)
            self.vbox.pack_start(self.bottom_box, False, True, 0)
            self.first_run = False
            
        self.add(self.vbox)
        self.show_all()

    def on_quit_clicked(self, quit_button):
        self.destroy()

    def on_about_clicked(self, widget):
        about = Gtk.AboutDialog(transient_for=self)
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file("about.xpm"));
        about.set_program_name("Gtk+: iOS Backup - Read Manifest.db")
        about.set_size_request(480, -1)
        about.set_version("Version 1.1.9")
        about.set_authors(_("Erich Küster, Krefeld/Germany\n"))
        about.set_copyright("Copyright © 2018-2021 Erich Küster. All rights reserved.")
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

    def on_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            domain, row_id = model[tree_iter][:2]
            treemodel = self.treeview.get_model()
            # delete data of an earlier run
            if (len(self.domain_items) > 0):
                del self.domain_items[:]
                # make place for new table rows
                treemodel.clear()
            if (row_id > 0):
                # remove vbox from main window
                self.remove(self.vbox)
                self.vbox.remove(self.bottom_box)
                self.vbox.remove(self.label_box)
                self.vbox.remove(self.scrolled_window)
                ''' self.vbox.remove(self.text_window) '''
                # filter out file info of the chosen domain
                indices = [0, 2, 3, 4]
                for record in self.records:
                    if (record[1] == domain):
                        selected_items = [record[index] for index in indices]
                        self.domain_items.append(selected_items)
                        # do not append file BLOB
                        treemodel.append(selected_items[0:3])
                self.context_id = self.status_bar.push(self.context_id,\
                    f(_('Chosen domain: {domain}')))
                self.vbox.pack_start(self.scrolled_window, False, True, 0)
                ''' self.vbox.pack_end(self.text_window) '''
                self.vbox.pack_start(self.label_box, True, True, 0)
                self.vbox.pack_end(self.bottom_box, False, True, 0)
                self.add(self.vbox)
                self.show_all()
        else:
            entry = combo.get_child()
            # but ignore any input (Enter is treated by signal 'activate' (see below)

    def on_entry_activate(self, entry):
        # on 'Enter' look for first row with domain containing the actual entry text
        self.context_id = self.status_bar.push(self.context_id,\
            _("no match found for entry"))
        search_term = entry.get_text()
        model = self.combo.get_model()
        first_match = 0
        column = 0
        for row in model:
            naked_domain = row[0]
            row_id = row[1]
            if search_term in naked_domain:
                # we do have a match
                self.combo.set_active(row_id-1)
                entry.set_text(naked_domain)
                self.context_id = self.status_bar.push(self.context_id,\
                    f(_('first match for entry is {naked_domain} at row {row_id}')))
                break

    def show_info_dialog(self, buffer):
        lines = tuple(buffer)
        report = "\n"
        dialog = InfoDialog(self)
        dialog.set_title(_("File Info Dialog"))
        markup = report.join(lines)
        self.dialog_label.set_markup(markup)
        response = dialog.run()
        dialog.destroy()
        # convert markup back to normal text
        if response == 100:
            # copy to clipboard
            text = re.sub('<[^<]+?>', '', markup)
            self.clipboard.set_text(text, -1)
            self.context_id = self.status_bar.push(self.context_id,\
                _("File Info copied to Clipboard, use Strg-V to retrieve."))

    def on_row_activated(self, treeview, path, column):
        model = self.treeview.get_model()
        tree_iter = model.get_iter(path)
        row = path[0]
        if tree_iter:
            file_id = model.get_value(tree_iter, 0)
            relative_path = model.get_value(tree_iter, 1)
            target = os.path.basename(relative_path)
            # flags 1 = RegularFile, 2 = Directory, 3 = Symlink
            flags = model.get_value(tree_iter, 2)
            # first have a look at the file BLOB
            domain_item = self.domain_items[row]
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
                self.context_id = self.status_bar.push(self.context_id,\
                    f(_("URL for backup'd file: {file_url}")))
                target_path = self.choose_folder_for_saving(\
                    _("Please choose a folder to copy file in"))
                if (target_path is None):
                    self.context_id = self.status_bar.push(self.context_id,\
                        _("No path for target file given, try again"))
                    return
                target_url = os.path.join(target_path,target)
                try:
                    with open(file_url, 'rb') as fo, open(target_url, 'wb') as fw:
                        while True:
                            piece = fo.read(1024)
                            if piece: 
                                fw.write(piece)
                            else:
                                break
                except EnvironmentError:
                    self.context_id = self.status_bar.push(self.context_id,\
                        _('Error during copying, good luck!'))
                finally:
                    self.context_id = self.status_bar.push(self.context_id,\
                        f(_('Copying to {target_url} complete, no errors')))
            else:
                self.context_id = self.status_bar.push(self.context_id,\
                    f(_('Saving rejected (wrong file type)')))

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
                            # print(f'subname: {subname}')
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

    def on_extract_domain_clicked(self, button):
        model = self.treeview.get_model()
        if len(model) == 0:
            self.context_id = self.status_bar.push(self.context_id,\
                _('Select domain first (no rows in model)'))
            return
        extract_path = self.choose_folder_for_saving(_("Please choose a folder for extracting files"))
        if (extract_path is None):
            self.context_id = self.status_bar.push(self.context_id,\
                _('No path for extracting files given, try again'))
            return
        elif len(os.listdir(extract_path)) != 0:
            self.context_id = self.status_bar.push(self.context_id,\
                _('Output directory is not empty!'))
            return
        # now we have a valid extract path
        self.context_id = self.status_bar.push(self.context_id,\
            f(_('Path to extract files: {extract_path}')))
        names = ['fileID', 'relativePath', 'flags']
        columns = dict()
        files = 0
        for row in model:
            for index, column in enumerate(row):
                columns[names[index]] = column
            if columns['flags'] != 1:
                continue
            else:
                # we have a regular file, get first two characters of file ID
                files += 1
                file_id = columns['fileID']
                file_hash = file_id[0:2]
                file_url = os.path.join(self.backup_path, file_hash, file_id)
                target_url = os.path.join(extract_path,columns['relativePath'])
                target_dirs = os.path.dirname(target_url)
                os.makedirs(target_dirs, exist_ok=True, mode=0o750)
                try:
                    with open(file_url, 'rb') as fo, open(target_url, 'wb') as fw:
                        while True:
                            piece = fo.read(1024)
                            if piece: 
                                fw.write(piece)
                            else:
                                break
                except EnvironmentError:
                    self.context_id = self.status_bar.push(self.context_id,\
                        _("An error occurred while copying"))
                finally:
                    self.context_id = self.status_bar.push(self.context_id,\
                        _('Copying ...'))
        if files > 0:
            self.context_id = self.status_bar.push(self.context_id,\
               f(_('{files} files extracted to: {extract_path}')))
        else:
            self.context_id = self.status_bar.push(self.context_id,\
               _('Nothing extracted (no regular files in domain)'))


    def choose_folder_for_saving(self, dialog_title):
        dialog = Gtk.FileChooserDialog(
            title=dialog_title,
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)
        # set default selection
        folder = None
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            folder = dialog.get_filename()
        dialog.destroy()
        return folder

    def on_export_csv_clicked(self, widget):
        # export data records into .csv file
        export_path = self.choose_folder_for_saving(_("Please choose a folder for exporting Manifest.csv"))
        if (export_path is None):
            self.context_id = self.status_bar.push(self.context_id,\
                _("No path for CSV file given, try again"))
            return
        export_url = os.path.join(export_path,'Manifest.csv')
        with open(export_url, 'w') as f:
            csv_writer = csv.writer(f, lineterminator='\n')
            for name in self.names:
                csv_writer.writerow(name)
            for record in self.records:
                csv_writer.writerow(record)
            self.context_id = self.status_bar.push(self.context_id,\
                f(_('Manifest.csv stored in folder {export_path}')))

    def on_destroy(self, widget):
        Gtk.main_quit()

# available translations
de = gettext.translation('ManifestDBView', localedir='locale', languages=['de'])
de.install()
# define _ shortcut for translations
_ = de.gettext # German
win = ManifestDBWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

