"""Main window for Tidskollen - Visual Time Timer."""
import math
import gettext
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib, Gdk

_ = gettext.gettext

PRESET_TIMES = [1, 2, 5, 10, 15, 20, 30, 45, 60]


class TimerDrawingArea(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.fraction = 1.0  # 1.0 = full, 0.0 = done
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.set_draw_func(self._draw)
        self.set_hexpand(True)
        self.set_vexpand(True)

    def _draw(self, area, cr, width, height):
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 20

        if radius < 10:
            return

        # Background circle (green = done)
        cr.set_source_rgb(0.15, 0.65, 0.40)
        cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
        cr.fill()

        # Remaining time wedge (red)
        if self.fraction > 0.001:
            # Interpolate red→green
            r = 0.75 * self.fraction + 0.15 * (1 - self.fraction)
            g = 0.11 * self.fraction + 0.65 * (1 - self.fraction)
            b = 0.18 * self.fraction + 0.40 * (1 - self.fraction)
            cr.set_source_rgb(r, g, b)
            start_angle = -math.pi / 2
            end_angle = start_angle + 2 * math.pi * self.fraction
            cr.move_to(center_x, center_y)
            cr.arc(center_x, center_y, radius, start_angle, end_angle)
            cr.close_path()
            cr.fill()

        # Border
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.set_line_width(3)
        cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
        cr.stroke()

        # Time text
        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        text = f"{mins}:{secs:02d}"
        cr.set_source_rgb(1, 1, 1)
        cr.select_font_face("Sans", 0, 1)
        font_size = radius * 0.4
        cr.set_font_size(font_size)
        extents = cr.text_extents(text)
        cr.move_to(center_x - extents.width / 2, center_y + extents.height / 2)
        cr.show_text(text)


class TidskollenWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, default_width=450, default_height=600,
                         title=_("Time Check"))
        self.running = False
        self.total_seconds = 300  # default 5 min
        self.remaining = self.total_seconds
        self.timer_id = None
        self._build_ui()
        self._start_clock()

    def _build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        header = Adw.HeaderBar()
        main_box.append(header)

        theme_btn = Gtk.Button(icon_name="weather-clear-night-symbolic",
                               tooltip_text=_("Toggle dark/light theme"))
        theme_btn.connect("clicked", self._toggle_theme)
        header.pack_end(theme_btn)

        fullscreen_btn = Gtk.Button(icon_name="view-fullscreen-symbolic",
                                    tooltip_text=_("Fullscreen"))
        fullscreen_btn.connect("clicked", lambda *_: self.get_application().activate_action("fullscreen"))
        header.pack_end(fullscreen_btn)

        menu = Gio.Menu()
        menu.append(_("Keyboard Shortcuts"), "app.shortcuts")
        menu.append(_("About Time Check"), "app.about")
        menu.append(_("Quit"), "app.quit")
        menu_btn = Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu)
        header.pack_end(menu_btn)

        # Timer display
        self.timer_area = TimerDrawingArea()
        self.timer_area.total_seconds = self.total_seconds
        self.timer_area.remaining_seconds = self.remaining
        main_box.append(self.timer_area)

        # Preset buttons
        preset_box = Gtk.Box(spacing=4, halign=Gtk.Align.CENTER)
        preset_box.set_margin_top(8)
        preset_box.set_margin_bottom(4)
        for mins in PRESET_TIMES:
            btn = Gtk.Button(label=f"{mins}m")
            btn.connect("clicked", self._on_preset, mins)
            preset_box.append(btn)
        main_box.append(preset_box)

        # Controls
        ctrl_box = Gtk.Box(spacing=12, halign=Gtk.Align.CENTER)
        ctrl_box.set_margin_top(8)
        ctrl_box.set_margin_bottom(8)

        self.start_btn = Gtk.Button(label=_("Start"))
        self.start_btn.add_css_class("suggested-action")
        self.start_btn.add_css_class("pill")
        self.start_btn.connect("clicked", self._on_start)
        ctrl_box.append(self.start_btn)

        self.stop_btn = Gtk.Button(label=_("Stop"))
        self.stop_btn.add_css_class("destructive-action")
        self.stop_btn.add_css_class("pill")
        self.stop_btn.set_sensitive(False)
        self.stop_btn.connect("clicked", self._on_stop)
        ctrl_box.append(self.stop_btn)

        reset_btn = Gtk.Button(label=_("Reset"))
        reset_btn.add_css_class("pill")
        reset_btn.connect("clicked", self._on_reset)
        ctrl_box.append(reset_btn)

        main_box.append(ctrl_box)

        # Status
        self.status_label = Gtk.Label(label="", xalign=0)
        self.status_label.add_css_class("dim-label")
        self.status_label.set_margin_start(12)
        self.status_label.set_margin_bottom(4)
        main_box.append(self.status_label)

    def _on_preset(self, btn, mins):
        if not self.running:
            self.total_seconds = mins * 60
            self.remaining = self.total_seconds
            self._update_display()

    def _on_start(self, btn):
        if not self.running and self.remaining > 0:
            self.running = True
            self.start_btn.set_sensitive(False)
            self.stop_btn.set_sensitive(True)
            self.timer_id = GLib.timeout_add(1000, self._tick)

    def _on_stop(self, btn):
        self.running = False
        self.start_btn.set_sensitive(True)
        self.stop_btn.set_sensitive(False)
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None

    def _on_reset(self, btn):
        self._on_stop(btn)
        self.remaining = self.total_seconds
        self._update_display()

    def _tick(self):
        if not self.running:
            return False
        self.remaining -= 1
        if self.remaining <= 0:
            self.remaining = 0
            self.running = False
            self.start_btn.set_sensitive(True)
            self.stop_btn.set_sensitive(False)
            self._update_display()
            self._on_timer_done()
            return False
        self._update_display()
        return True

    def _update_display(self):
        if self.total_seconds > 0:
            self.timer_area.fraction = self.remaining / self.total_seconds
        else:
            self.timer_area.fraction = 0
        self.timer_area.remaining_seconds = self.remaining
        self.timer_area.queue_draw()

    def _on_timer_done(self):
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=_("Time's up!"),
            body=_("The timer has finished."),
        )
        dialog.add_response("ok", _("OK"))
        dialog.present()

    def _toggle_theme(self, btn):
        mgr = Adw.StyleManager.get_default()
        if mgr.get_dark():
            mgr.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            mgr.set_color_scheme(Adw.ColorScheme.FORCE_DARK)

    def _start_clock(self):
        GLib.timeout_add_seconds(1, self._update_clock)
        self._update_clock()

    def _update_clock(self):
        now = GLib.DateTime.new_now_local()
        self.status_label.set_label(now.format("%Y-%m-%d %H:%M:%S"))
        return True
