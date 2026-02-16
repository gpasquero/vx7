"""VX7 visual constants and styling.

Defines all colors, fonts, and dimensions used across the GUI to replicate
the distinctive look of the Yamaha DX7 synthesizer.

The DX7 has a dark brown/charcoal body with brownish-tan membrane buttons,
a classic green-on-dark LCD display, light blue/cyan accent buttons for
certain functions, and a metallic silver strip at the top bearing the
manufacturer branding.
"""

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

# Body and panel
BODY_COLOR = "#2D2520"         # Dark brown body
PANEL_COLOR = "#1A1714"        # Darker panel areas
BORDER_COLOR = "#3D3530"       # Subtle border / groove lines

# Membrane buttons
BUTTON_COLOR = "#8B7D6B"      # Membrane button default (brownish tan)
BUTTON_ACTIVE = "#A69279"     # Button hover / active state
BUTTON_PRESSED = "#6B5D4B"   # Button depressed state
BUTTON_TEXT = "#1A1714"        # Dark text on buttons

# LCD display
LCD_BG = "#0A1A0A"            # LCD background (very dark green)
LCD_TEXT = "#00FF41"           # LCD text (bright green)
LCD_DIM = "#003300"            # LCD dim / inactive segments
LCD_GLOW = "#00CC33"          # LCD text glow layer
LCD_BORDER_OUTER = "#0E0E0E"  # LCD bezel outer edge
LCD_BORDER_INNER = "#1A1A1A"  # LCD bezel inner edge

# Accent colors
ACCENT_BLUE = "#4A90B8"       # Blue accent buttons (function keys)
ACCENT_BLUE_ACTIVE = "#6AB0D8"
ACCENT_ORANGE = "#D4722A"     # Orange accent (store, special controls)
ACCENT_ORANGE_ACTIVE = "#E8924A"

# Sliders and controls
SLIDER_BG = "#3D3530"         # Slider track background
SLIDER_FG = "#C4A882"         # Slider handle / fill
SLIDER_GROOVE = "#252018"     # Slider groove inset

# Header
HEADER_COLOR = "#C0C0C0"      # Silver header strip
HEADER_TEXT = "#2D2520"        # Dark text on silver header
HEADER_HIGHLIGHT = "#D8D8D8"  # Highlight line on header strip
HEADER_SHADOW = "#909090"     # Shadow line on header strip

# Labels and text
LABEL_COLOR = "#A09080"        # Label text on body
SECTION_LABEL_COLOR = "#C4B8A8"  # Section header label text
GROUP_BG = "#241E1A"          # Slightly lighter background for grouped sections

# Piano keyboard
WHITE_KEY = "#F5F0E8"         # Piano key white
WHITE_KEY_PRESSED = "#D0C8B8"  # White key when depressed
BLACK_KEY = "#1A1714"         # Piano key black
BLACK_KEY_PRESSED = "#3A3530"  # Black key when depressed
KEY_BORDER = "#888070"        # Key outline

# LEDs
LED_ON = "#FF3030"            # LED active (red)
LED_OFF = "#3A1010"           # LED inactive
LED_GLOW = "#FF6060"          # LED glow halo

# Operator display
OP_ON_COLOR = "#4A90B8"       # Operator enabled color
OP_OFF_COLOR = "#3D3530"      # Operator disabled color
OP_CARRIER_COLOR = "#D4722A"  # Carrier operator highlight
OP_MODULATOR_COLOR = "#4A90B8"  # Modulator operator highlight
ALGO_LINE_COLOR = "#A09080"   # Algorithm connection lines
ALGO_BG = "#1A1714"           # Algorithm display background

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

LCD_FONT = ("Courier", 18, "bold")
LCD_FONT_SMALL = ("Courier", 11)
LABEL_FONT = ("Helvetica", 8)
LABEL_FONT_BOLD = ("Helvetica", 8, "bold")
SECTION_FONT = ("Helvetica", 9, "bold")
BUTTON_FONT = ("Helvetica", 9, "bold")
BUTTON_FONT_SMALL = ("Helvetica", 7, "bold")
HEADER_FONT = ("Helvetica", 24, "bold")
HEADER_FONT_SUB = ("Helvetica", 10)
PRESET_NUM_FONT = ("Courier", 10, "bold")
KEY_LABEL_FONT = ("Helvetica", 6)

# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------

# Overall window
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 580

# Header strip
HEADER_HEIGHT = 36

# LCD display
LCD_WIDTH = 320
LCD_HEIGHT = 80
LCD_CHAR_WIDTH = 16    # Characters per line
LCD_LINES = 2          # Number of text lines
LCD_BEZEL = 6          # Bezel border thickness

# Algorithm display
ALGO_DISPLAY_WIDTH = 120
ALGO_DISPLAY_HEIGHT = 90

# Operator buttons
OP_BUTTON_SIZE = 32
OP_LED_RADIUS = 4

# Membrane buttons
MEMBRANE_BUTTON_WIDTH = 58
MEMBRANE_BUTTON_HEIGHT = 26
MEMBRANE_BUTTON_RADIUS = 3    # Corner rounding

# Preset buttons
PRESET_BUTTON_SIZE = 28

# Piano keyboard
KEYBOARD_HEIGHT = 100
WHITE_KEY_WIDTH = 24
WHITE_KEY_HEIGHT = 92
BLACK_KEY_WIDTH = 15
BLACK_KEY_HEIGHT = 55

# Slider
SLIDER_WIDTH = 26
SLIDER_HEIGHT = 140
SLIDER_HANDLE_HEIGHT = 14

# Spacing
SECTION_PAD_X = 8
SECTION_PAD_Y = 6
BUTTON_GAP = 4

# ---------------------------------------------------------------------------
# DX7 Algorithm definitions (operator connection topologies)
# ---------------------------------------------------------------------------
# Each algorithm is a list of connections and carriers.
# Format: dict with 'connections' (list of (from_op, to_op) tuples)
# and 'carriers' (set of operator numbers that output to the DAC).
# Operators are numbered 1-6.
#
# These 32 algorithms match the real DX7.
# ---------------------------------------------------------------------------

ALGORITHMS = {
    1:  {"connections": [(2, 1), (4, 3), (6, 5), (3, 1)], "carriers": {1}},
    2:  {"connections": [(2, 1), (4, 3), (6, 5), (3, 1)], "carriers": {1}},
    3:  {"connections": [(2, 1), (3, 1), (5, 4), (6, 4)], "carriers": {1, 4}},
    4:  {"connections": [(2, 1), (3, 1), (5, 4), (6, 5)], "carriers": {1, 4}},
    5:  {"connections": [(2, 1), (4, 3), (6, 5)], "carriers": {1, 3, 5}},
    6:  {"connections": [(2, 1), (4, 3), (6, 5)], "carriers": {1, 3, 5}},
    7:  {"connections": [(2, 1), (4, 3), (5, 3), (6, 5)], "carriers": {1, 3}},
    8:  {"connections": [(2, 1), (4, 3), (6, 5), (5, 3)], "carriers": {1, 3}},
    9:  {"connections": [(2, 1), (3, 1), (5, 4), (6, 4)], "carriers": {1, 4}},
    10: {"connections": [(2, 1), (4, 3), (5, 3), (6, 3)], "carriers": {1, 3}},
    11: {"connections": [(2, 1), (4, 3), (6, 5), (5, 3)], "carriers": {1, 3}},
    12: {"connections": [(2, 1), (3, 1), (4, 1), (6, 5)], "carriers": {1, 5}},
    13: {"connections": [(2, 1), (4, 3), (5, 3), (6, 3)], "carriers": {1, 3}},
    14: {"connections": [(2, 1), (4, 3), (5, 3), (6, 5)], "carriers": {1, 3}},
    15: {"connections": [(2, 1), (4, 3), (5, 3)], "carriers": {1, 3}},
    16: {"connections": [(2, 1), (3, 1), (5, 4), (6, 5), (4, 1)], "carriers": {1}},
    17: {"connections": [(2, 1), (3, 1), (5, 4), (4, 1)], "carriers": {1}},
    18: {"connections": [(2, 1), (3, 1), (4, 1), (6, 5)], "carriers": {1, 5}},
    19: {"connections": [(2, 1), (4, 3), (5, 3), (6, 3)], "carriers": {1, 3}},
    20: {"connections": [(2, 1), (3, 1), (5, 4), (6, 4)], "carriers": {1, 4}},
    21: {"connections": [(2, 1), (3, 1), (5, 4), (6, 4)], "carriers": {1, 4}},
    22: {"connections": [(2, 1), (4, 3), (5, 3), (6, 3)], "carriers": {1, 3}},
    23: {"connections": [(2, 1), (4, 3), (5, 3)], "carriers": {1, 3}},
    24: {"connections": [(2, 1), (4, 3), (5, 3)], "carriers": {1, 3}},
    25: {"connections": [(2, 1), (4, 3)], "carriers": {1, 3}},
    26: {"connections": [(2, 1), (4, 3), (5, 3)], "carriers": {1, 3}},
    27: {"connections": [(2, 1), (4, 3)], "carriers": {1, 3}},
    28: {"connections": [(3, 2), (5, 4), (6, 5)], "carriers": {1, 2, 4}},
    29: {"connections": [(2, 1), (5, 4), (6, 5)], "carriers": {1, 4}},
    30: {"connections": [(3, 2), (5, 4)], "carriers": {1, 2, 4}},
    31: {"connections": [(2, 1)], "carriers": {1, 3, 4, 5}},
    32: {"connections": [], "carriers": {1, 2, 3, 4, 5, 6}},
}

# ---------------------------------------------------------------------------
# DX7 operator layout positions for algorithm diagrams
# ---------------------------------------------------------------------------
# Standard 2-row layout:  Row 0 (top) = modulators, Row 1 (bottom) = carriers
# Each operator has an (x, y) position in normalized 0-1 space within the
# algorithm display canvas.

ALGO_OP_POSITIONS = {
    # op_num: (x_fraction, y_fraction) within the algo display canvas
    6: (0.15, 0.20),
    5: (0.35, 0.20),
    4: (0.55, 0.20),
    3: (0.75, 0.20),
    2: (0.35, 0.70),
    1: (0.75, 0.70),
}
