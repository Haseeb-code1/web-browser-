"""
Nova Browser Theme Definition.
This file defines the global color palette, typography, border radiuses,
and spacing tokens for the deep space dark theme and light theme.
"""

# Nova Browser — Dark Theme (default)
BACKGROUND_PRIMARY   = "#0D0F1A"   # Deepest dark (main window bg)
BACKGROUND_SECONDARY = "#13151F"   # Slightly lighter (panels, sidebar)
BACKGROUND_TERTIARY  = "#1A1D2E"   # Cards, dropdowns, menus
BACKGROUND_ELEVATED  = "#1F2235"   # Hovered items, active tabs
BACKGROUND_GLASS     = "rgba(20, 22, 35, 0.85)"  # Glass panels

ACCENT_PRIMARY   = "#6C63FF"   # Electric violet (main accent)
ACCENT_SECONDARY = "#00D4FF"   # Cyan blue (secondary, links)
ACCENT_SUCCESS   = "#00E5A0"   # Mint green (success, connected)
ACCENT_WARNING   = "#FFB830"   # Amber (warnings)
ACCENT_DANGER    = "#FF4757"   # Red (close, errors)

TEXT_PRIMARY   = "#E8E9F3"   # Near white (main text)
TEXT_SECONDARY = "#8B8FA8"   # Muted (subtitles, labels)
TEXT_TERTIARY  = "#555870"   # Very muted (placeholders)
TEXT_ACCENT    = "#6C63FF"   # Accent text (links, active)

BORDER_SUBTLE  = "rgba(255,255,255,0.06)"  # Hairline borders
BORDER_MEDIUM  = "rgba(255,255,255,0.10)"  # Visible borders
BORDER_STRONG  = "rgba(108, 99, 255, 0.4)" # Accent borders

# Light Theme (toggle in settings)
LIGHT_BG       = "#F5F5FA"
LIGHT_SURFACE  = "#FFFFFF"
LIGHT_ACCENT   = "#6C63FF"
LIGHT_TEXT     = "#1A1A2E"

# Spacing System
SPACING_BASE   = 4
SPACING_MICRO  = 4
SPACING_SMALL  = 8
SPACING_MEDIUM = 12
SPACING_LARGE  = 16
SPACING_XL     = 24

# Border Radiuses
RADIUS_SMALL   = 6
RADIUS_MEDIUM  = 10
RADIUS_LARGE   = 14
RADIUS_FULL    = 999

# Typography Fonts
FONT_FAMILY    = '"Segoe UI Variable", "Inter", "SF Pro", system-ui'
