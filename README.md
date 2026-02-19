# Tidskollen

Visual Time Timer for classrooms and children with autism.

> **Målgrupp / Target audience:** Barn och vuxna med autism, ADHD, språkstörning (DLD)
> och andra funktionsnedsättningar som behöver visuellt tidsstöd. Den krympande cirkeln
> gör abstrakt tid konkret och synlig. Perfekt för klassrum, hemmet och habilitering.
>
> **For:** Children and adults with autism spectrum disorder (ASD), ADHD, developmental
> language disorder (DLD), and other disabilities who need visual time support. The
> shrinking circle makes abstract time concrete and visible. Perfect for classrooms,
> home, and rehabilitation settings.

![Screenshot](screenshots/screenshot.png)

## Features

- Large shrinking circle (red → green) for visual countdown
- Configurable time presets (1–60 min)
- Sound alert on completion
- Fullscreen mode for classroom display
- Dark/light theme toggle

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
