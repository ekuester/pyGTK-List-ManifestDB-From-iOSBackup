import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# method to create the toolbar
def create(self):
    # a toolbar
    toolbar = Gtk.Toolbar()
    # which is the primary toolbar of the application
    toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
    # toolbar.set_toolbar_style(Gtk.TOOLBAR_BOTH)
    labels = [_('Open'), _('Quit'), _('About')]
    icons = ['document-open', 'application-exit', 'help-about']
    tooltips = [_('Open data base'), _('Exit program'), _('About program')]
    actions = ['open', 'quit', 'about']
    for i, label in enumerate(labels):
        icon = Gtk.Image.new_from_icon_name(icons[i], Gtk.IconSize.LARGE_TOOLBAR)
        button = Gtk.ToolButton.new(icon, labels[i])
        button.set_tooltip_text(tooltips[i])
        button.set_is_important(True)
        toolbar.insert(button, i)
        button.show()
        button.set_action_name(f'app.{actions[i]}')
    # create horizontal space
    toolitem_space = Gtk.SeparatorToolItem()
    toolitem_space.set_expand(True)
    toolbar.insert(toolitem_space, 2)
    # show the _toolbar
    toolbar.show()
    # return the complete toolbar
    return toolbar

