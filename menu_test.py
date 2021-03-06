from gi.repository import Gtk, Gdk
import json
import signal

from pprint import pprint

class MenuTest(Gtk.Window):
	"""docstring for MenuTest"""
	def __init__(self):
		super(MenuTest, self).__init__(title="Menu Test")
		self.connect("delete-event", Gtk.main_quit)

		self.spawn_menubar('hammer.menu')

		self.set_default_size(200, 0)
		self.show_all()

	def spawn_menubar(self, resource):
		menubar = Gtk.MenuBar()

		with open(resource) as resource:
			self.walk_menu(json.load(resource), menubar)

		self.add(menubar)
		return menubar

	def walk_menu(self, definition, widget):
		for menu in definition:
			if not 'mnemonic' in menu:
				menu['mnemonic'] = ''
			if not 'args' in menu:
				menu['args'] = ()
			if 'children' in menu:
				sub_menu = self.spawn_menu(
					caption  = menu['caption'],
					widget   = widget,
					mnemonic = menu['mnemonic']
				)
				self.walk_menu(menu['children'], sub_menu)
			else:
				menuitem = Gtk.MenuItem

				if 'checked' in menu:
					menuitem = Gtk.CheckMenuItem

				if not 'command' in menu:
					if '-' == menu['caption']:
						menuitem = Gtk.SeparatorMenuItem
						menu['command'] = ''
					elif 'id' in menu:
						# Insert these elements anyway, they may be used
						# as an id achor point for complex menu generators
						menu['command'] = ''
					else:
						raise NameError(
							'Menu item "%s" missing command.' % menu['caption']
						)

				action = self.spawn_action(
					caption  = menu['caption'],
					widget   = widget,
					mnemonic = menu['mnemonic'],
					action   = self.resolve_callable(menu['command'], menu['args']),
					menuitem = menuitem
				)

	def spawn_menu(self, caption, widget, mnemonic):
		menu = Gtk.Menu()
		item = Gtk.MenuItem(caption)
		item.set_submenu(menu)
		if mnemonic:
			item.set_use_underline(True)
			item.set_label(self.menu_mnemonic(caption, mnemonic))
		widget.append(item)
		return menu

	def spawn_action(self, caption, widget, mnemonic, action, menuitem=Gtk.MenuItem):
		if menuitem == Gtk.SeparatorMenuItem:
			return self.spawn_sep(widget)
		item = menuitem(caption)
		item.connect("activate", action)
		if mnemonic:
			item.set_use_underline(True)
			item.set_label(self.menu_mnemonic(caption, mnemonic))
		widget.append(item)
		return action

	def spawn_sep(self, widget):
		sep = Gtk.SeparatorMenuItem()
		widget.append(sep)

		return sep

	def menu_mnemonic(self, caption, mnemonic):
		index = caption.lower().find(mnemonic.lower())
		return caption[0:index] + '_' + caption[index:]

	def resolve_callable(self, command, args):
		return lambda x: pprint((command, args))

	def main(self):
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		Gtk.main()

if __name__ == "__main__":
	window = MenuTest()
	window.main()

