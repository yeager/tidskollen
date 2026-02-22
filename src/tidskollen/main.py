import os
"""Tidskollen - Visual Time Timer."""
import sys
import gettext
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
from tidskollen import __version__
from tidskollen.window import TidskollenWindow
from tidskollen.accessibility import apply_large_text

TEXTDOMAIN = "tidskollen"
gettext.textdomain(TEXTDOMAIN)
_ = gettext.gettext



def _settings_path():
    xdg = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    d = os.path.join(xdg, "tidskollen")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "settings.json")

def _load_settings():
    p = _settings_path()
    if os.path.exists(p):
        import json
        with open(p) as f:
            return json.load(f)
    return {}

def _save_settings(s):
    import json
    with open(_settings_path(), "w") as f:
        json.dump(s, f, indent=2)

class TidskollenApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="se.yeager.tidskollen",
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self):
        apply_large_text()
        win = self.props.active_window or TidskollenWindow(application=self)
        win.present()
        if not self.settings.get("welcome_shown"):
            self._show_welcome(win)


    def do_startup(self):
        Adw.Application.do_startup(self)
        self._setup_actions()

    def _setup_actions(self):
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *_: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Control>q"])

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)

        shortcuts_action = Gio.SimpleAction.new("shortcuts", None)
        shortcuts_action.connect("activate", self._on_shortcuts)
        self.add_action(shortcuts_action)
        self.set_accels_for_action("app.shortcuts", ["<Control>slash"])

        fullscreen_action = Gio.SimpleAction.new("fullscreen", None)
        fullscreen_action.connect("activate", self._on_fullscreen)
        self.add_action(fullscreen_action)
        self.set_accels_for_action("app.fullscreen", ["F11"])

    def _on_fullscreen(self, *_args):
        win = self.props.active_window
        if win:
            if win.is_fullscreen():
                win.unfullscreen()
            else:
                win.fullscreen()

    def _on_about(self, *_args):
        about = Adw.AboutDialog(
            application_name=_("Time Check"),
            application_icon="tidskollen",
            version=__version__,
            developer_name="Daniel Nylander",
            website="https://github.com/yeager/tidskollen",
            issue_url="https://github.com/yeager/tidskollen/issues",
            translate_url="https://app.transifex.com/danielnylander/tidskollen",
            license_type=Gtk.License.GPL_3_0,
            developers=["Daniel Nylander"],
            copyright="© 2026 Daniel Nylander",
        )
        about.present(self.props.active_window)

    def _on_shortcuts(self, *_args):
        builder = Gtk.Builder()
        builder.add_from_string('''
        <interface>
          <object class="GtkShortcutsWindow" id="shortcuts">
            <property name="modal">true</property>
            <child><object class="GtkShortcutsSection"><child><object class="GtkShortcutsGroup">
              <property name="title" translatable="yes">General</property>
              <child><object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Quit</property>
                <property name="accelerator">&lt;Control&gt;q</property>
              </object></child>
              <child><object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Fullscreen</property>
                <property name="accelerator">F11</property>
              </object></child>
            </object></child></object></child>
          </object>
        </interface>''')
        win = builder.get_object("shortcuts")
        win.set_transient_for(self.props.active_window)
        win.present()


def main():
    app = TidskollenApp()
    app.run(sys.argv)

    # ── Welcome Dialog ───────────────────────────────────────

    def _show_welcome(self, win):
        dialog = Adw.Dialog()
        dialog.set_title(_("Welcome"))
        dialog.set_content_width(420)
        dialog.set_content_height(480)

        page = Adw.StatusPage()
        page.set_icon_name("tidskollen")
        page.set_title(_("Welcome to Time Tracker"))
        page.set_description(_(
            "A visual countdown timer for children.\n\n✓ Large, clear countdown display\n✓ Set custom time intervals\n✓ Audio alerts when time is up\n✓ Easy to understand for all ages"
        ))

        btn = Gtk.Button(label=_("Get Started"))
        btn.add_css_class("suggested-action")
        btn.add_css_class("pill")
        btn.set_halign(Gtk.Align.CENTER)
        btn.set_margin_top(12)
        btn.connect("clicked", self._on_welcome_close, dialog)
        page.set_child(btn)

        box = Adw.ToolbarView()
        hb = Adw.HeaderBar()
        hb.set_show_title(False)
        box.add_top_bar(hb)
        box.set_content(page)
        dialog.present(win)

    def _on_welcome_close(self, btn, dialog):
        self.settings["welcome_shown"] = True
        _save_settings(self.settings)
        dialog.close()

