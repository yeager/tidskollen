# Tidskollen

Visual Time Timer for classrooms and children with autism.

![Screenshot](screenshots/screenshot.png)

## Features

Large shrinking circle (red→green), configurable time presets (1-60 min), sound alert on completion, fullscreen mode for classroom display.

## Requirements

- Python 3.10+
- GTK4 / libadwaita
- PyGObject

## Installation

```bash
# Install dependencies (Fedora/RHEL)
sudo dnf install python3-gobject gtk4 libadwaita

# Install dependencies (Debian/Ubuntu)
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1

# Run from source
PYTHONPATH=src python3 -c "from tidskollen.main import main; main()"
```

## License

GPL-3.0-or-later

## Author

Daniel Nylander

## Links

- [GitHub](https://github.com/yeager/tidskollen)
- [Issues](https://github.com/yeager/tidskollen/issues)
- [Translations](https://app.transifex.com/danielnylander/tidskollen)
