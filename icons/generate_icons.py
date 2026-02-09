"""
generate_icons.py

Generate SVG icons for each UI theme.
Run this script to regenerate icons after modifying colors or designs.

Each theme gets two icon variants:
- Normal: for unselected/default button state
- Selected: inverted contrast for selected/checked button state
"""

import os

# Theme color definitions with normal and selected (inverted) variants
THEMES = {
    "Foundation": {
        "normal": {"stroke": "#FEFEFE", "fill": "none", "accent": "#1779BA"},
        "selected": {"stroke": "#1A1A1A", "fill": "none", "accent": "#1779BA"},
    },
    "Bulma": {
        "normal": {"stroke": "#363636", "fill": "none", "accent": "#00D1B2"},
        "selected": {"stroke": "#FFFFFF", "fill": "none", "accent": "#00D1B2"},
    },
    "Bauhaus": {
        "normal": {"stroke": "#212121", "fill": "none", "accent": "#E53935"},
        "selected": {"stroke": "#FFFFFF", "fill": "none", "accent": "#FDD835"},
    },
    "Neumorphism": {
        "normal": {"stroke": "#4B5563", "fill": "none", "accent": "#6366F1"},
        "selected": {"stroke": "#FFFFFF", "fill": "none", "accent": "#6366F1"},
    },
    "Materialize": {
        "normal": {"stroke": "#212121", "fill": "none", "accent": "#26A69A"},
        "selected": {"stroke": "#FFFFFF", "fill": "none", "accent": "#26A69A"},
    },
    "Tailwind": {
        "normal": {"stroke": "#374151", "fill": "none", "accent": "#3B82F6"},
        "selected": {"stroke": "#FFFFFF", "fill": "none", "accent": "#3B82F6"},
    },
    "Bootstrap": {
        "normal": {"stroke": "#212529", "fill": "none", "accent": "#0D6EFD"},
        "selected": {"stroke": "#FFFFFF", "fill": "none", "accent": "#0D6EFD"},
    },
}

# SVG icon templates (24x24 viewBox)
ICONS = {
    "select": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M4 4 L4 18 L8 14 L12 20 L14 19 L10 13 L16 13 Z" stroke="{stroke}" stroke-width="1.5" fill="{accent}" stroke-linejoin="round"/>
</svg>''',

    "rect": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <rect x="3" y="5" width="18" height="14" stroke="{stroke}" stroke-width="2" fill="{fill}" rx="0"/>
</svg>''',

    "rrect": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <rect x="3" y="5" width="18" height="14" stroke="{stroke}" stroke-width="2" fill="{fill}" rx="4"/>
</svg>''',

    "ellipse": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <ellipse cx="12" cy="12" rx="9" ry="7" stroke="{stroke}" stroke-width="2" fill="{fill}"/>
</svg>''',

    "line": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <line x1="4" y1="20" x2="20" y2="4" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
  <circle cx="4" cy="20" r="2" fill="{accent}"/>
  <circle cx="20" cy="4" r="2" fill="{accent}"/>
</svg>''',

    "text": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M5 6 L5 4 L19 4 L19 6" stroke="{stroke}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="12" y1="4" x2="12" y2="20" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
  <line x1="9" y1="20" x2="15" y2="20" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
</svg>''',

    "open": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M3 6 L3 18 L21 18 L21 8 L12 8 L10 6 Z" stroke="{stroke}" stroke-width="1.5" fill="{fill}" stroke-linejoin="round"/>
  <path d="M3 10 L7 10 L21 10" stroke="{stroke}" stroke-width="1.5"/>
</svg>''',

    "clear": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M6 6 L18 6 L17 20 L7 20 Z" stroke="{stroke}" stroke-width="1.5" fill="{fill}" stroke-linejoin="round"/>
  <line x1="4" y1="6" x2="20" y2="6" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
  <path d="M9 6 L9 4 L15 4 L15 6" stroke="{stroke}" stroke-width="1.5" fill="none"/>
  <line x1="10" y1="10" x2="10" y2="16" stroke="{stroke}" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="14" y1="10" x2="14" y2="16" stroke="{stroke}" stroke-width="1.5" stroke-linecap="round"/>
</svg>''',

    "model": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <circle cx="12" cy="12" r="3" stroke="{stroke}" stroke-width="2" fill="{fill}"/>
  <path d="M12 2 L12 5" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
  <path d="M12 19 L12 22" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
  <path d="M4.22 4.22 L6.34 6.34" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
  <path d="M17.66 17.66 L19.78 19.78" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
  <path d="M2 12 L5 12" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
  <path d="M19 12 L22 12" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
  <path d="M4.22 19.78 L6.34 17.66" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
  <path d="M17.66 6.34 L19.78 4.22" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
</svg>''',

    "extract": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M12 2 L14 8 L12 7 L10 8 Z" fill="{accent}" stroke="{stroke}" stroke-width="1"/>
  <path d="M22 12 L16 14 L17 12 L16 10 Z" fill="{accent}" stroke="{stroke}" stroke-width="1"/>
  <path d="M12 22 L10 16 L12 17 L14 16 Z" fill="{accent}" stroke="{stroke}" stroke-width="1"/>
  <path d="M2 12 L8 10 L7 12 L8 14 Z" fill="{accent}" stroke="{stroke}" stroke-width="1"/>
  <circle cx="12" cy="12" r="3" stroke="{accent}" stroke-width="2" fill="none"/>
</svg>''',

    "hide_png": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M2 12 C5 7 9 5 12 5 C15 5 19 7 22 12 C19 17 15 19 12 19 C9 19 5 17 2 12 Z" stroke="{stroke}" stroke-width="1.5" fill="{fill}"/>
  <circle cx="12" cy="12" r="3" stroke="{stroke}" stroke-width="1.5" fill="{accent}"/>
  <line x1="4" y1="20" x2="20" y2="4" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
</svg>''',

    "show_png": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M2 12 C5 7 9 5 12 5 C15 5 19 7 22 12 C19 17 15 19 12 19 C9 19 5 17 2 12 Z" stroke="{stroke}" stroke-width="1.5" fill="{fill}"/>
  <circle cx="12" cy="12" r="3" stroke="{stroke}" stroke-width="1.5" fill="{accent}"/>
</svg>''',

    "focus_on": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <!-- Cord -->
  <line x1="12" y1="1" x2="12" y2="5" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
  <!-- Lamp shade -->
  <path d="M6 5 L12 5 L18 5 L16 14 L8 14 Z" stroke="{stroke}" stroke-width="1.5" fill="{accent}"/>
  <!-- Bulb glow effect -->
  <ellipse cx="12" cy="15" rx="3" ry="2" fill="{accent}" opacity="0.6"/>
  <!-- Light rays -->
  <line x1="12" y1="17" x2="12" y2="22" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>
  <line x1="6" y1="16" x2="3" y2="20" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>
  <line x1="18" y1="16" x2="21" y2="20" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>
  <line x1="8" y1="17" x2="6" y2="22" stroke="{accent}" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="16" y1="17" x2="18" y2="22" stroke="{accent}" stroke-width="1.5" stroke-linecap="round"/>
</svg>''',

    "focus_off": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <!-- Cord -->
  <line x1="12" y1="1" x2="12" y2="5" stroke="{stroke}" stroke-width="2" stroke-linecap="round"/>
  <!-- Lamp shade -->
  <path d="M6 5 L12 5 L18 5 L16 14 L8 14 Z" stroke="{stroke}" stroke-width="1.5" fill="{fill}"/>
  <!-- Bulb (off) -->
  <ellipse cx="12" cy="15" rx="2" ry="1.5" stroke="{stroke}" stroke-width="1" fill="{fill}"/>
</svg>''',

    "import_link": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M14 3 L14 8 L19 8" stroke="{stroke}" stroke-width="1.5" fill="{fill}" stroke-linejoin="round"/>
  <path d="M19 8 L14 3 L5 3 L5 21 L19 21 L19 8 Z" stroke="{stroke}" stroke-width="1.5" fill="{fill}" stroke-linejoin="round"/>
  <path d="M9 13 L15 13" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>
  <path d="M12 10 L12 16" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>
  <circle cx="9" cy="13" r="1.5" fill="{accent}"/>
  <circle cx="15" cy="13" r="1.5" fill="{accent}"/>
</svg>''',

    "undo": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M4 10 L9 5 L9 8 C14 8 18 10 18 15 C18 18 15 20 12 20 L12 17 C14 17 15 16 15 15 C15 12 12 11 9 11 L9 14 Z" stroke="{stroke}" stroke-width="1.5" fill="{accent}" stroke-linejoin="round"/>
</svg>''',

    "redo": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M20 10 L15 5 L15 8 C10 8 6 10 6 15 C6 18 9 20 12 20 L12 17 C10 17 9 16 9 15 C9 12 12 11 15 11 L15 14 Z" stroke="{stroke}" stroke-width="1.5" fill="{accent}" stroke-linejoin="round"/>
</svg>''',

    "zoom_region": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <circle cx="10" cy="10" r="6" stroke="{stroke}" stroke-width="2" fill="{fill}"/>
  <line x1="14.5" y1="14.5" x2="20" y2="20" stroke="{stroke}" stroke-width="2.5" stroke-linecap="round"/>
  <rect x="7" y="7" width="6" height="6" stroke="{accent}" stroke-width="1.5" fill="none" stroke-dasharray="2,1"/>
</svg>''',

    "zoom_fit": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M3 8 L3 3 L8 3" stroke="{stroke}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M21 8 L21 3 L16 3" stroke="{stroke}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M3 16 L3 21 L8 21" stroke="{stroke}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M21 16 L21 21 L16 21" stroke="{stroke}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="7" y="7" width="10" height="10" stroke="{accent}" stroke-width="1.5" fill="{fill}"/>
</svg>''',

    "hexagon": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <polygon points="6,4 18,4 22,12 18,20 6,20 2,12" stroke="{stroke}" stroke-width="2" fill="{fill}" stroke-linejoin="round"/>
</svg>''',

    "cylinder": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <ellipse cx="12" cy="6" rx="7" ry="3" stroke="{stroke}" stroke-width="2" fill="{fill}"/>
  <path d="M5 6 L5 18" stroke="{stroke}" stroke-width="2"/>
  <path d="M19 6 L19 18" stroke="{stroke}" stroke-width="2"/>
  <path d="M5 18 A7 3 0 0 0 19 18" stroke="{stroke}" stroke-width="2" fill="none"/>
</svg>''',

    "blockarrow": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <polygon points="2,8 14,8 14,4 22,12 14,20 14,16 2,16" stroke="{stroke}" stroke-width="2" fill="{fill}" stroke-linejoin="round"/>
</svg>''',
}


def generate_icons():
    """Generate all icons for all themes (normal and selected variants)."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for theme_name, variants in THEMES.items():
        theme_dir = os.path.join(base_dir, theme_name)
        os.makedirs(theme_dir, exist_ok=True)

        for variant_name, colors in variants.items():
            for icon_name, template in ICONS.items():
                svg_content = template.format(**colors)

                # Normal icons: icon_name.svg, Selected icons: icon_name_selected.svg
                if variant_name == "normal":
                    filename = f"{icon_name}.svg"
                else:
                    filename = f"{icon_name}_{variant_name}.svg"

                icon_path = os.path.join(theme_dir, filename)

                with open(icon_path, "w", encoding="utf-8") as f:
                    f.write(svg_content)

                print(f"Created: {icon_path}")

    print("\nIcon generation complete!")


if __name__ == "__main__":
    generate_icons()
