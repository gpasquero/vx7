"""VX7 main control panel.

Replicates the Yamaha DX7 Mk1 front-panel layout using tkinter Canvas widgets.
The panel uses a 2-row layout with pitch bend and modulation wheels to the left
of the keyboard, and a 7-segment LED patch number display.

    ROW 1: 7-SEG | LCD | ALGORITHM | OPERATOR SELECT | MASTER
    ROW 2: DATA ENTRY | MEMORY SELECT | FUNCTION | PARAMETERS
    KEYBOARD: WHEELS | PIANO KEYS (C1-C6)

- Silver header strip with VX7 branding
- 7-segment 2-digit red LED patch number display
- LCD display with green-on-dark text
- Algorithm topology diagram
- Operator on/off toggles with LED indicators
- Master volume and tune sliders
- Data entry slider with up/down buttons
- Preset/memory selection grid (32 buttons in 4 rows of 8)
- Function buttons (STORE, EDIT, COMPARE, ALGO+, ALGO-, INIT)
- Parameter editing buttons (3x3 grid)
- Pitch bend and modulation wheels
- Five-octave clickable piano keyboard (C1-C6)
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

from .styles import (
    # Colors
    BODY_COLOR, PANEL_COLOR, BORDER_COLOR,
    BUTTON_COLOR, BUTTON_ACTIVE, BUTTON_PRESSED, BUTTON_TEXT,
    LCD_BG, LCD_TEXT,
    ACCENT_BLUE, ACCENT_BLUE_ACTIVE,
    ACCENT_ORANGE, ACCENT_ORANGE_ACTIVE,
    SLIDER_BG, SLIDER_FG, SLIDER_GROOVE,
    HEADER_COLOR, HEADER_TEXT, HEADER_HIGHLIGHT, HEADER_SHADOW,
    LABEL_COLOR, SECTION_LABEL_COLOR, GROUP_BG,
    WHITE_KEY, WHITE_KEY_PRESSED, BLACK_KEY, BLACK_KEY_PRESSED, KEY_BORDER,
    LED_ON, LED_OFF, LED_GLOW,
    OP_ON_COLOR, OP_OFF_COLOR, OP_CARRIER_COLOR, OP_MODULATOR_COLOR,
    ALGO_LINE_COLOR, ALGO_BG,
    SEVEN_SEG_BG, SEVEN_SEG_ON, SEVEN_SEG_OFF, SEVEN_SEG_GLOW,
    WHEEL_COLOR, WHEEL_HIGHLIGHT, WHEEL_TRACK,
    # Fonts
    LCD_FONT, LABEL_FONT, LABEL_FONT_BOLD, SECTION_FONT,
    BUTTON_FONT, BUTTON_FONT_SMALL,
    HEADER_FONT, HEADER_FONT_SUB, PRESET_NUM_FONT, KEY_LABEL_FONT,
    # Dimensions
    WINDOW_WIDTH, WINDOW_HEIGHT, HEADER_HEIGHT,
    ALGO_DISPLAY_WIDTH, ALGO_DISPLAY_HEIGHT,
    OP_BUTTON_SIZE, OP_LED_RADIUS,
    MEMBRANE_BUTTON_WIDTH, MEMBRANE_BUTTON_HEIGHT, MEMBRANE_BUTTON_RADIUS,
    PRESET_BUTTON_SIZE,
    KEYBOARD_HEIGHT, WHITE_KEY_WIDTH, WHITE_KEY_HEIGHT,
    BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT,
    SLIDER_WIDTH, SLIDER_HEIGHT, SLIDER_HANDLE_HEIGHT,
    SECTION_PAD_X, SECTION_PAD_Y, BUTTON_GAP,
    SEVEN_SEG_WIDTH, SEVEN_SEG_HEIGHT,
    WHEEL_AREA_WIDTH,
    # Algorithm data
    ALGORITHMS,
)
from .display import LCDDisplay


# ======================================================================
# Callback type aliases
# ======================================================================
NoteOnCallback = Callable[[int, int], None]     # (note, velocity)
NoteOffCallback = Callable[[int], None]          # (note,)
PresetCallback = Callable[[int], None]           # (index,)
ParamCallback = Callable[[str, object], None]    # (param_name, value)


# ======================================================================
# 7-segment digit encoding
# ======================================================================
# Segments: a=top, b=top-right, c=bottom-right, d=bottom,
#           e=bottom-left, f=top-left, g=middle
SEVEN_SEG_DIGITS = {
    0: (1, 1, 1, 1, 1, 1, 0),
    1: (0, 1, 1, 0, 0, 0, 0),
    2: (1, 1, 0, 1, 1, 0, 1),
    3: (1, 1, 1, 1, 0, 0, 1),
    4: (0, 1, 1, 0, 0, 1, 1),
    5: (1, 0, 1, 1, 0, 1, 1),
    6: (1, 0, 1, 1, 1, 1, 1),
    7: (1, 1, 1, 0, 0, 0, 0),
    8: (1, 1, 1, 1, 1, 1, 1),
    9: (1, 1, 1, 1, 0, 1, 1),
}


# ======================================================================
# Helper: rounded rectangle on a Canvas
# ======================================================================

def _rounded_rect(
    canvas: tk.Canvas,
    x0: float, y0: float, x1: float, y1: float,
    radius: float = 4,
    **kwargs,
) -> int:
    """Draw a rounded rectangle and return the canvas item id."""
    r = radius
    points = [
        x0 + r, y0,
        x1 - r, y0,
        x1, y0,
        x1, y0 + r,
        x1, y1 - r,
        x1, y1,
        x1 - r, y1,
        x0 + r, y1,
        x0, y1,
        x0, y1 - r,
        x0, y0 + r,
        x0, y0,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


# ======================================================================
# MembraneButton -- a single DX7-style membrane button on a Canvas
# ======================================================================

class MembraneButton:
    """A single membrane-style button drawn on a parent Canvas.

    Parameters
    ----------
    canvas : tk.Canvas
        The canvas to draw on.
    x, y : float
        Top-left corner position.
    width, height : float
        Button dimensions.
    text : str
        Label text.
    color : str
        Fill color.
    active_color : str
        Color when hovered / active.
    command : callable or None
        Invoked on click.
    toggle : bool
        If True the button sticks on/off.
    font : tuple
        Font spec.
    text_color : str
        Label text color.
    """

    def __init__(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        width: float = MEMBRANE_BUTTON_WIDTH,
        height: float = MEMBRANE_BUTTON_HEIGHT,
        text: str = "",
        color: str = BUTTON_COLOR,
        active_color: str = BUTTON_ACTIVE,
        command: Optional[Callable] = None,
        toggle: bool = False,
        font: tuple = BUTTON_FONT,
        text_color: str = BUTTON_TEXT,
    ) -> None:
        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.text = text
        self.color = color
        self.active_color = active_color
        self.command = command
        self.toggle = toggle
        self._state = False  # toggle state

        # Draw button body.
        self._body = _rounded_rect(
            canvas, x, y, x + width, y + height,
            radius=MEMBRANE_BUTTON_RADIUS,
            fill=color, outline=BORDER_COLOR, width=1,
        )

        # Shadow line at bottom for 3-D look.
        self._shadow = canvas.create_line(
            x + 3, y + height - 1, x + width - 3, y + height - 1,
            fill="#3A3530", width=1,
        )

        # Highlight line at top.
        self._highlight = canvas.create_line(
            x + 3, y + 1, x + width - 3, y + 1,
            fill="#4A4540", width=1,
        )

        # Text label.
        self._label = canvas.create_text(
            x + width / 2, y + height / 2,
            text=text, font=font, fill=text_color,
            anchor="center",
        )

        # Bind events to all parts.
        for item in (self._body, self._label):
            canvas.tag_bind(item, "<Enter>", self._on_enter)
            canvas.tag_bind(item, "<Leave>", self._on_leave)
            canvas.tag_bind(item, "<ButtonPress-1>", self._on_press)
            canvas.tag_bind(item, "<ButtonRelease-1>", self._on_release)

    # Interaction -------------------------------------------------------

    def _on_enter(self, _event: tk.Event) -> None:
        self.canvas.itemconfigure(self._body, fill=self.active_color)

    def _on_leave(self, _event: tk.Event) -> None:
        fill = self.active_color if (self.toggle and self._state) else self.color
        self.canvas.itemconfigure(self._body, fill=fill)

    def _on_press(self, _event: tk.Event) -> None:
        self.canvas.itemconfigure(self._body, fill=BUTTON_PRESSED)

    def _on_release(self, _event: tk.Event) -> None:
        if self.toggle:
            self._state = not self._state
        fill = self.active_color if (self.toggle and self._state) else self.color
        self.canvas.itemconfigure(self._body, fill=fill)
        if self.command:
            self.command()

    # Public API --------------------------------------------------------

    @property
    def state(self) -> bool:
        return self._state

    @state.setter
    def state(self, value: bool) -> None:
        self._state = bool(value)
        fill = self.active_color if self._state else self.color
        self.canvas.itemconfigure(self._body, fill=fill)

    def set_color(self, color: str, active_color: str | None = None) -> None:
        self.color = color
        if active_color:
            self.active_color = active_color
        fill = self.active_color if (self.toggle and self._state) else self.color
        self.canvas.itemconfigure(self._body, fill=fill)


# ======================================================================
# VX7Panel -- the full synthesizer control panel
# ======================================================================

class VX7Panel(tk.Frame):
    """Main DX7-style control panel with 2-row layout.

    Parameters
    ----------
    parent : tk.Widget
        Parent widget (typically the root window).
    """

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        super().__init__(parent, bg=BODY_COLOR, **kwargs)

        # Callbacks -- set externally.
        self._on_note_on: Optional[NoteOnCallback] = None
        self._on_note_off: Optional[NoteOffCallback] = None
        self._on_preset_change: Optional[PresetCallback] = None
        self._on_param_change: Optional[ParamCallback] = None

        # State.
        self._current_algo = 1
        self._operator_states = [True] * 6  # All ops enabled.
        self._current_preset = 0
        self._pressed_keys: set[int] = set()
        self._volume = 0.8

        # Wheel state.
        self._pitch_bend = 0.5   # 0.5 = center
        self._mod_wheel = 0.0    # 0.0 = bottom

        # Build the panel sections.
        self._build_header()
        self._build_main_area()
        self._build_keyboard()

    # ==================================================================
    # Callback setters
    # ==================================================================

    def set_note_callbacks(
        self,
        on_note_on: Optional[NoteOnCallback],
        on_note_off: Optional[NoteOffCallback],
    ) -> None:
        self._on_note_on = on_note_on
        self._on_note_off = on_note_off

    def set_preset_callback(self, cb: Optional[PresetCallback]) -> None:
        self._on_preset_change = cb

    def set_param_callback(self, cb: Optional[ParamCallback]) -> None:
        self._on_param_change = cb

    # ==================================================================
    # Header strip
    # ==================================================================

    def _build_header(self) -> None:
        """Silver strip at the top with VX7 branding."""
        self._header = tk.Canvas(
            self, width=WINDOW_WIDTH, height=HEADER_HEIGHT,
            bg=HEADER_COLOR, highlightthickness=0,
        )
        self._header.pack(fill="x", side="top")

        # Top highlight line.
        self._header.create_line(
            0, 1, WINDOW_WIDTH, 1, fill=HEADER_HIGHLIGHT, width=1,
        )
        # Bottom shadow line.
        self._header.create_line(
            0, HEADER_HEIGHT - 1, WINDOW_WIDTH, HEADER_HEIGHT - 1,
            fill=HEADER_SHADOW, width=1,
        )

        # VX7 branding on the left.
        self._header.create_text(
            20, HEADER_HEIGHT // 2,
            text="VX7", font=HEADER_FONT, fill=HEADER_TEXT,
            anchor="w",
        )

        # Subtitle on the right side.
        self._header.create_text(
            WINDOW_WIDTH - 20, HEADER_HEIGHT // 2 + 2,
            text="VIRTUAL DX7 SYNTHESIZER",
            font=HEADER_FONT_SUB, fill="#505050",
            anchor="e",
        )

        # Decorative line separating branding from subtitle.
        self._header.create_line(
            100, HEADER_HEIGHT // 2,
            WINDOW_WIDTH - 250, HEADER_HEIGHT // 2,
            fill=HEADER_SHADOW, width=1,
        )

    # ==================================================================
    # Main area (everything between header and keyboard)
    # ==================================================================

    def _build_main_area(self) -> None:
        """Build the controls area below the header.

        Two-row layout:
        ROW 1: 7-SEG | LCD | ALGORITHM | OPERATOR SELECT | MASTER
        ROW 2: DATA ENTRY | MEMORY SELECT | FUNCTION | PARAMETERS
        """
        main_h = WINDOW_HEIGHT - HEADER_HEIGHT - KEYBOARD_HEIGHT
        self._main_canvas = tk.Canvas(
            self, width=WINDOW_WIDTH, height=main_h,
            bg=BODY_COLOR, highlightthickness=0,
        )
        self._main_canvas.pack(fill="both", side="top")

        # Separator between row 1 and row 2.
        row2_y = 195
        self._main_canvas.create_line(
            10, row2_y - 5, WINDOW_WIDTH - 10, row2_y - 5,
            fill=BORDER_COLOR, width=1,
        )

        # Build Row 1 sections.
        self._build_seven_segment_display()
        self._build_lcd_section()
        self._build_algorithm_section()
        self._build_operator_section()
        self._build_master_section()

        # Build Row 2 sections.
        self._build_data_entry_section()
        self._build_memory_section()
        self._build_function_section()
        self._build_parameter_section()

    # ------------------------------------------------------------------
    # ROW 1: 7-Segment Display (far left)
    # ------------------------------------------------------------------

    def _build_seven_segment_display(self) -> None:
        """Two-digit 7-segment red LED display showing patch number (01-32)."""
        sx = 15
        sy = 15

        # Section label.
        self._main_canvas.create_text(
            sx + SEVEN_SEG_WIDTH // 2, sy - 2,
            text="PATCH", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="s",
        )

        # Create the 7-segment canvas.
        self._seg_canvas = tk.Canvas(
            self._main_canvas,
            width=SEVEN_SEG_WIDTH, height=SEVEN_SEG_HEIGHT,
            bg=SEVEN_SEG_BG, highlightthickness=1,
            highlightbackground=BORDER_COLOR,
        )
        self._main_canvas.create_window(
            sx, sy, window=self._seg_canvas, anchor="nw",
        )

        # Draw initial display (patch 01).
        self._seg_items: list[list[int]] = [[], []]  # Two digits, each with 7 segments
        self._draw_seven_seg_digits()
        self.set_patch_number(1)

        # UP/DOWN arrow buttons below the 7-seg display for preset navigation.
        arrow_w = 36
        arrow_h = 24
        arrow_x = sx + (SEVEN_SEG_WIDTH - arrow_w) // 2
        arrow_y = sy + SEVEN_SEG_HEIGHT + 6

        MembraneButton(
            self._main_canvas,
            arrow_x, arrow_y,
            width=arrow_w, height=arrow_h,
            text="\u25B2", color=ACCENT_BLUE, active_color=ACCENT_BLUE_ACTIVE,
            command=lambda: self.navigate_preset(1),
            font=("Helvetica", 10, "bold"),
            text_color="#FFFFFF",
        )

        MembraneButton(
            self._main_canvas,
            arrow_x, arrow_y + arrow_h + 3,
            width=arrow_w, height=arrow_h,
            text="\u25BC", color=ACCENT_BLUE, active_color=ACCENT_BLUE_ACTIVE,
            command=lambda: self.navigate_preset(-1),
            font=("Helvetica", 10, "bold"),
            text_color="#FFFFFF",
        )

    def _draw_seven_seg_digits(self) -> None:
        """Create the segment line items for both digits on the 7-seg canvas."""
        c = self._seg_canvas
        # Digit dimensions.
        dw = 18   # digit width
        dh = 32   # digit height
        seg_w = 3  # segment line width

        # Positions: digit 0 (tens) at left, digit 1 (ones) at right.
        digit_x_positions = [12, 48]
        digit_y = (SEVEN_SEG_HEIGHT - dh) // 2

        for d_idx, dx in enumerate(digit_x_positions):
            dy = digit_y
            segs = []

            # Segment a: horizontal top
            segs.append(c.create_line(
                dx + 2, dy, dx + dw - 2, dy,
                fill=SEVEN_SEG_OFF, width=seg_w, capstyle="round",
            ))
            # Segment b: vertical top-right
            segs.append(c.create_line(
                dx + dw, dy + 2, dx + dw, dy + dh // 2 - 2,
                fill=SEVEN_SEG_OFF, width=seg_w, capstyle="round",
            ))
            # Segment c: vertical bottom-right
            segs.append(c.create_line(
                dx + dw, dy + dh // 2 + 2, dx + dw, dy + dh - 2,
                fill=SEVEN_SEG_OFF, width=seg_w, capstyle="round",
            ))
            # Segment d: horizontal bottom
            segs.append(c.create_line(
                dx + 2, dy + dh, dx + dw - 2, dy + dh,
                fill=SEVEN_SEG_OFF, width=seg_w, capstyle="round",
            ))
            # Segment e: vertical bottom-left
            segs.append(c.create_line(
                dx, dy + dh // 2 + 2, dx, dy + dh - 2,
                fill=SEVEN_SEG_OFF, width=seg_w, capstyle="round",
            ))
            # Segment f: vertical top-left
            segs.append(c.create_line(
                dx, dy + 2, dx, dy + dh // 2 - 2,
                fill=SEVEN_SEG_OFF, width=seg_w, capstyle="round",
            ))
            # Segment g: horizontal middle
            segs.append(c.create_line(
                dx + 2, dy + dh // 2, dx + dw - 2, dy + dh // 2,
                fill=SEVEN_SEG_OFF, width=seg_w, capstyle="round",
            ))

            self._seg_items[d_idx] = segs

    def set_patch_number(self, num: int) -> None:
        """Update the 7-segment display to show a patch number (1-32).

        Parameters
        ----------
        num : int
            Patch number to display (1-32).
        """
        num = max(1, min(32, num))
        tens = num // 10
        ones = num % 10

        c = self._seg_canvas
        for seg_idx, on in enumerate(SEVEN_SEG_DIGITS.get(tens, (0,) * 7)):
            color = SEVEN_SEG_ON if on else SEVEN_SEG_OFF
            c.itemconfigure(self._seg_items[0][seg_idx], fill=color)

        for seg_idx, on in enumerate(SEVEN_SEG_DIGITS.get(ones, (0,) * 7)):
            color = SEVEN_SEG_ON if on else SEVEN_SEG_OFF
            c.itemconfigure(self._seg_items[1][seg_idx], fill=color)

    def update_patch_number(self, num: int) -> None:
        """Public API alias for set_patch_number."""
        self.set_patch_number(num)

    # ------------------------------------------------------------------
    # ROW 1: LCD Display
    # ------------------------------------------------------------------

    def _build_lcd_section(self) -> None:
        """LCD display section."""
        sx = 110
        sy = 8

        # Section label.
        self._main_canvas.create_text(
            sx, sy, text="DISPLAY", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="nw",
        )

        # LCD display.
        self._lcd = LCDDisplay(self._main_canvas)
        self._main_canvas.create_window(
            sx, sy + 14, window=self._lcd, anchor="nw",
        )

        # Default content.
        self._lcd.set_patch(1, "INIT VOICE")
        self._lcd.set_line2("VX7 Ready")

    # ------------------------------------------------------------------
    # ROW 1: Algorithm Display
    # ------------------------------------------------------------------

    def _build_algorithm_section(self) -> None:
        """Algorithm topology diagram."""
        sx = 450
        sy = 8

        self._main_canvas.create_text(
            sx, sy, text="ALGORITHM", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="nw",
        )

        # Algorithm number shown next to the label, outside the diagram.
        self._algo_num_label = self._main_canvas.create_text(
            sx + ALGO_DISPLAY_WIDTH, sy -5,
            text="1", font=("Courier", 16, "bold"),
            fill=LCD_TEXT, anchor="ne",
        )

        self._algo_canvas = tk.Canvas(
            self._main_canvas,
            width=ALGO_DISPLAY_WIDTH, height=ALGO_DISPLAY_HEIGHT,
            bg=ALGO_BG, highlightthickness=1,
            highlightbackground=BORDER_COLOR,
        )
        self._main_canvas.create_window(
            sx, sy + 14, window=self._algo_canvas, anchor="nw",
        )

        self.draw_algorithm(1)

    # ------------------------------------------------------------------
    # ROW 1: Operator Select
    # ------------------------------------------------------------------

    def _build_operator_section(self) -> None:
        """6 operator toggle buttons with LED indicators."""
        sx = 600
        sy = 8

        self._main_canvas.create_text(
            sx, sy, text="OPERATOR SELECT", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="nw",
        )

        op_btn_y = sy + 14

        # Background panel for operator buttons.
        op_panel_w = 6 * (OP_BUTTON_SIZE + BUTTON_GAP) + 12
        op_panel_h = OP_BUTTON_SIZE + 28
        _rounded_rect(
            self._main_canvas,
            sx - 4, op_btn_y - 4,
            sx + op_panel_w, op_btn_y + op_panel_h,
            radius=4, fill=GROUP_BG, outline=BORDER_COLOR,
        )

        self._op_buttons: list[MembraneButton] = []
        self._op_leds: list[int] = []

        for i in range(6):
            bx = sx + i * (OP_BUTTON_SIZE + BUTTON_GAP) + 6
            by = op_btn_y + 18

            # LED indicator above button.
            led = self._main_canvas.create_oval(
                bx + OP_BUTTON_SIZE // 2 - OP_LED_RADIUS,
                by - 10 - OP_LED_RADIUS,
                bx + OP_BUTTON_SIZE // 2 + OP_LED_RADIUS,
                by - 10 + OP_LED_RADIUS,
                fill=LED_ON, outline=LED_GLOW, width=1,
            )
            self._op_leds.append(led)

            def make_op_toggle(idx: int):
                def toggle():
                    self._toggle_operator(idx)
                return toggle

            btn = MembraneButton(
                self._main_canvas,
                bx, by,
                width=OP_BUTTON_SIZE, height=OP_BUTTON_SIZE,
                text=str(i + 1),
                color=ACCENT_BLUE, active_color=ACCENT_BLUE_ACTIVE,
                command=make_op_toggle(i),
                toggle=True,
                font=BUTTON_FONT,
                text_color="#FFFFFF",
            )
            btn.state = True
            self._op_buttons.append(btn)

        # Operator level label below.
        self._main_canvas.create_text(
            sx + op_panel_w // 2, op_btn_y + op_panel_h + 6,
            text="1     2     3     4     5     6",
            font=LABEL_FONT, fill=LABEL_COLOR, anchor="n",
        )

    # ------------------------------------------------------------------
    # ROW 1: Master (Volume + Tune sliders)
    # ------------------------------------------------------------------

    def _build_master_section(self) -> None:
        """Volume slider and master tune slider on the far right."""
        sx = 880
        sy = 8

        self._main_canvas.create_text(
            sx + 70, sy, text="MASTER", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="n",
        )

        panel_w = 150
        panel_h = SLIDER_HEIGHT + 50
        _rounded_rect(
            self._main_canvas,
            sx, sy + 14,
            sx + panel_w, sy + 14 + panel_h,
            radius=4, fill=GROUP_BG, outline=BORDER_COLOR,
        )

        # Volume slider.
        vol_x = sx + 25
        self._main_canvas.create_text(
            vol_x + SLIDER_WIDTH // 2, sy + 28,
            text="VOLUME", font=LABEL_FONT_BOLD,
            fill=LABEL_COLOR, anchor="n",
        )
        self._build_slider(vol_x, sy + 42, "volume", self._volume)

        # Tune slider.
        tune_x = sx + 95
        self._main_canvas.create_text(
            tune_x + SLIDER_WIDTH // 2, sy + 28,
            text="TUNE", font=LABEL_FONT_BOLD,
            fill=LABEL_COLOR, anchor="n",
        )
        self._build_slider(tune_x, sy + 42, "tune", 0.5)

    # ------------------------------------------------------------------
    # ROW 2: Data Entry slider + up/down buttons
    # ------------------------------------------------------------------

    def _build_data_entry_section(self) -> None:
        """Vertical DATA ENTRY slider."""
        sx = 15
        sy = 200

        # Section label.
        self._main_canvas.create_text(
            sx + 25, sy, text="DATA ENTRY", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="n",
        )

        # Background panel.
        panel_w = 52
        panel_h = SLIDER_HEIGHT + 20
        _rounded_rect(
            self._main_canvas,
            sx, sy + 14,
            sx + panel_w, sy + 14 + panel_h,
            radius=4, fill=GROUP_BG, outline=BORDER_COLOR,
        )

        # Data entry slider.
        slider_x = sx + (panel_w - SLIDER_WIDTH) // 2
        slider_y = sy + 24
        self._build_slider(slider_x, slider_y, "data_entry", 0.5)

    # ------------------------------------------------------------------
    # ROW 2: Memory Select (32 preset buttons in 4 rows of 8)
    # ------------------------------------------------------------------

    def _build_memory_section(self) -> None:
        """32 preset buttons in 4 rows of 8."""
        sx = 80
        sy = 200

        # Section label.
        self._main_canvas.create_text(
            sx, sy, text="MEMORY SELECT", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="nw",
        )

        bs = PRESET_BUTTON_SIZE + 2  # button + gap
        preset_y = sy + 14

        # Background panel for presets.
        panel_w = 8 * bs + 8
        panel_h = 4 * bs + 8
        _rounded_rect(
            self._main_canvas,
            sx - 4, preset_y - 4,
            sx + panel_w, preset_y + panel_h,
            radius=4, fill=GROUP_BG, outline=BORDER_COLOR,
        )

        self._preset_buttons: list[MembraneButton] = []
        for i in range(32):
            col = i % 8
            row = i // 8
            bx = sx + col * bs + 4
            by = preset_y + row * bs + 4

            def make_preset_cb(idx: int):
                def cb():
                    self._select_preset(idx)
                return cb

            btn = MembraneButton(
                self._main_canvas,
                bx, by,
                width=PRESET_BUTTON_SIZE,
                height=PRESET_BUTTON_SIZE,
                text=str(i + 1),
                color=BUTTON_COLOR, active_color=BUTTON_ACTIVE,
                command=make_preset_cb(i),
                font=PRESET_NUM_FONT,
            )
            self._preset_buttons.append(btn)

        # Highlight the initially selected preset.
        self._highlight_preset(0)

    # ------------------------------------------------------------------
    # ROW 2: Function buttons
    # ------------------------------------------------------------------

    def _build_function_section(self) -> None:
        """Two rows of function buttons: STORE/EDIT/COMPARE, ALGO+/ALGO-/INIT."""
        sx = 370
        sy = 200

        self._main_canvas.create_text(
            sx, sy, text="FUNCTION", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="nw",
        )

        bw = MEMBRANE_BUTTON_WIDTH + 2
        bh = MEMBRANE_BUTTON_HEIGHT + 2
        func_y = sy + 14

        # Background panel.
        func_panel_w = 3 * bw + 8
        func_panel_h = 2 * bh + 12
        _rounded_rect(
            self._main_canvas,
            sx - 4, func_y - 4,
            sx + func_panel_w, func_y + func_panel_h,
            radius=4, fill=GROUP_BG, outline=BORDER_COLOR,
        )

        self._func_buttons: list[MembraneButton] = []

        # Row 1: STORE, EDIT, COMPARE
        row1_names = ["STORE", "EDIT", "COMPARE"]
        for i, name in enumerate(row1_names):
            bx = sx + i * bw + 4
            by = func_y + 4

            is_accent = name == "STORE"
            color = ACCENT_ORANGE if is_accent else ACCENT_BLUE
            active = ACCENT_ORANGE_ACTIVE if is_accent else ACCENT_BLUE_ACTIVE

            def make_func_cb(func_name: str):
                def cb():
                    self._handle_function(func_name)
                return cb

            btn = MembraneButton(
                self._main_canvas,
                bx, by,
                width=MEMBRANE_BUTTON_WIDTH,
                height=MEMBRANE_BUTTON_HEIGHT,
                text=name,
                color=color, active_color=active,
                command=make_func_cb(name),
                font=BUTTON_FONT_SMALL,
                text_color="#FFFFFF",
            )
            self._func_buttons.append(btn)

        # Row 2: ALGO+, ALGO-, INIT
        row2_names = ["ALGO+", "ALGO-", "INIT"]
        for i, name in enumerate(row2_names):
            bx = sx + i * bw + 4
            by = func_y + bh + 8

            is_accent = name == "INIT"
            color = ACCENT_ORANGE if is_accent else ACCENT_BLUE
            active = ACCENT_ORANGE_ACTIVE if is_accent else ACCENT_BLUE_ACTIVE

            def make_func_cb2(func_name: str):
                def cb():
                    self._handle_function(func_name)
                return cb

            btn = MembraneButton(
                self._main_canvas,
                bx, by,
                width=MEMBRANE_BUTTON_WIDTH,
                height=MEMBRANE_BUTTON_HEIGHT,
                text=name,
                color=color, active_color=active,
                command=make_func_cb2(name),
                font=BUTTON_FONT_SMALL,
                text_color="#FFFFFF",
            )
            self._func_buttons.append(btn)

    # ------------------------------------------------------------------
    # ROW 2: Parameter buttons (3x3 grid)
    # ------------------------------------------------------------------

    def _build_parameter_section(self) -> None:
        """3x3 grid of parameter editing buttons."""
        sx = 570
        sy = 200

        self._main_canvas.create_text(
            sx, sy, text="PARAMETERS", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="nw",
        )

        param_names = [
            "OUTPUT\nLEVEL", "FREQ\nCOARSE", "FREQ\nFINE",
            "ENVELOPE", "KBD\nSCALE", "MOD\nSENS",
            "DETUNE", "ENV\nRATE", "ENV\nLEVEL",
        ]

        cols = 3
        rows = 3
        bw = MEMBRANE_BUTTON_WIDTH + 2
        bh = MEMBRANE_BUTTON_HEIGHT + 2
        panel_w = cols * bw + 8
        panel_h = rows * bh + 8

        param_btn_y = sy + 14
        _rounded_rect(
            self._main_canvas,
            sx - 4, param_btn_y - 4,
            sx + panel_w, param_btn_y + panel_h,
            radius=4, fill=GROUP_BG, outline=BORDER_COLOR,
        )

        self._param_buttons: list[MembraneButton] = []
        for i, name in enumerate(param_names):
            col = i % cols
            row = i // cols
            bx = sx + col * bw + 4
            by = param_btn_y + row * bh + 4

            def make_param_cb(param_name: str):
                def cb():
                    if self._on_param_change:
                        self._on_param_change(param_name, None)
                    self._lcd.set_line2(param_name.replace("\n", " "))
                return cb

            btn = MembraneButton(
                self._main_canvas,
                bx, by,
                width=MEMBRANE_BUTTON_WIDTH,
                height=MEMBRANE_BUTTON_HEIGHT,
                text=name,
                color=BUTTON_COLOR, active_color=BUTTON_ACTIVE,
                command=make_param_cb(name),
                font=BUTTON_FONT_SMALL,
            )
            self._param_buttons.append(btn)

    # ------------------------------------------------------------------
    # Operator toggle logic
    # ------------------------------------------------------------------

    def _toggle_operator(self, index: int) -> None:
        """Toggle an operator on/off."""
        self._operator_states[index] = not self._operator_states[index]
        led_color = LED_ON if self._operator_states[index] else LED_OFF
        glow = LED_GLOW if self._operator_states[index] else LED_OFF
        self._main_canvas.itemconfigure(
            self._op_leds[index], fill=led_color, outline=glow,
        )
        self.draw_algorithm(self._current_algo)
        if self._on_param_change:
            self._on_param_change(
                f"op{index + 1}_enable",
                self._operator_states[index],
            )

    def _handle_function(self, name: str) -> None:
        """Dispatch function button presses."""
        if name == "ALGO+":
            new_algo = min(32, self._current_algo + 1)
            self.draw_algorithm(new_algo)
            self._lcd.set_line2(f"ALGORITHM {new_algo:>2d}")
            if self._on_param_change:
                self._on_param_change("algorithm", new_algo)
        elif name == "ALGO-":
            new_algo = max(1, self._current_algo - 1)
            self.draw_algorithm(new_algo)
            self._lcd.set_line2(f"ALGORITHM {new_algo:>2d}")
            if self._on_param_change:
                self._on_param_change("algorithm", new_algo)
        elif name == "INIT":
            self._lcd.set_line2("INIT VOICE")
            self._lcd.flash()
            if self._on_param_change:
                self._on_param_change("init", True)
        elif name == "STORE":
            self._lcd.set_line2("STORE...")
            self._lcd.flash(80)
        elif name == "EDIT":
            self._lcd.set_line2("EDIT MODE")
        elif name == "COMPARE":
            self._lcd.set_line2("COMPARE")
        if self._on_param_change:
            self._on_param_change(f"func_{name.lower()}", True)

    # ------------------------------------------------------------------
    # Algorithm drawing
    # ------------------------------------------------------------------

    def draw_algorithm(self, algo_num: int) -> None:
        """Draw the operator connection topology for the given algorithm.

        Parameters
        ----------
        algo_num : int
            Algorithm number (1-32).
        """
        self._current_algo = algo_num
        c = self._algo_canvas
        w = ALGO_DISPLAY_WIDTH
        h = ALGO_DISPLAY_HEIGHT

        # Clear previous drawing (except the number label).
        c.delete("algo_drawing")

        algo = ALGORITHMS.get(algo_num, ALGORITHMS[1])
        connections = algo["connections"]
        carriers = algo["carriers"]

        # Compute operator positions.
        # Carriers on bottom row, modulators stacked above.
        op_positions: dict[int, tuple[float, float]] = {}
        carrier_list = sorted(carriers)
        modulator_list = sorted(set(range(1, 7)) - carriers)

        # Bottom row: carriers, evenly spaced.
        nc = len(carrier_list)
        for i, op in enumerate(carrier_list):
            x = (i + 0.5) / max(nc, 1) * (w - 30) + 15
            y = h - 20
            op_positions[op] = (x, y)

        # Top row: modulators, evenly spaced.
        nm = len(modulator_list)
        for i, op in enumerate(modulator_list):
            x = (i + 0.5) / max(nm, 1) * (w - 30) + 15
            y = 26
            op_positions[op] = (x, y)

        # Draw connections first (below the boxes).
        for from_op, to_op in connections:
            if from_op in op_positions and to_op in op_positions:
                fx, fy = op_positions[from_op]
                tx, ty = op_positions[to_op]
                c.create_line(
                    fx, fy, tx, ty,
                    fill=ALGO_LINE_COLOR, width=1,
                    arrow="last", arrowshape=(6, 7, 3),
                    tags="algo_drawing",
                )

        # Draw operator boxes.
        box_r = 9
        for op_num in range(1, 7):
            if op_num not in op_positions:
                continue
            ox, oy = op_positions[op_num]
            is_carrier = op_num in carriers
            fill = OP_CARRIER_COLOR if is_carrier else OP_MODULATOR_COLOR

            if not self._operator_states[op_num - 1]:
                fill = OP_OFF_COLOR

            c.create_rectangle(
                ox - box_r, oy - box_r, ox + box_r, oy + box_r,
                fill=fill, outline=LABEL_COLOR, width=1,
                tags="algo_drawing",
            )
            c.create_text(
                ox, oy, text=str(op_num),
                font=("Helvetica", 7, "bold"), fill="#FFFFFF",
                tags="algo_drawing",
            )

        # Update the algorithm number (label lives on main_canvas, not algo_canvas).
        self._main_canvas.itemconfigure(self._algo_num_label, text=str(algo_num))
        self._main_canvas.tag_raise(self._algo_num_label)

    # ------------------------------------------------------------------
    # Slider builder (shared by DATA ENTRY and MASTER sections)
    # ------------------------------------------------------------------

    def _build_slider(
        self, x: float, y: float, name: str, initial: float,
    ) -> None:
        """Draw a vertical slider on the main canvas."""
        c = self._main_canvas
        sw = SLIDER_WIDTH
        sh = SLIDER_HEIGHT

        # Groove.
        groove_x = x + sw // 2 - 2
        c.create_rectangle(
            groove_x, y, groove_x + 4, y + sh,
            fill=SLIDER_GROOVE, outline=BORDER_COLOR,
        )

        # Track fill.
        fill_h = int(sh * (1 - initial))
        fill_id = c.create_rectangle(
            groove_x, y + fill_h, groove_x + 4, y + sh,
            fill=SLIDER_FG, outline="",
        )

        # Handle.
        handle_y = y + fill_h - SLIDER_HANDLE_HEIGHT // 2
        handle = c.create_rectangle(
            x + 2, handle_y,
            x + sw - 2, handle_y + SLIDER_HANDLE_HEIGHT,
            fill=SLIDER_FG, outline=LABEL_COLOR, width=1,
        )

        # Handle grip lines.
        for dy in range(-2, 4, 2):
            c.create_line(
                x + 6, handle_y + SLIDER_HANDLE_HEIGHT // 2 + dy,
                x + sw - 6, handle_y + SLIDER_HANDLE_HEIGHT // 2 + dy,
                fill=BUTTON_TEXT, width=1, tags=f"slider_grip_{name}",
            )

        # Drag interaction.
        slider_data = {
            "name": name, "fill_id": fill_id, "handle": handle,
            "y_top": y, "y_bot": y + sh, "x": x, "sw": sw,
        }

        def on_press(event, data=slider_data):
            data["dragging"] = True

        def on_drag(event, data=slider_data):
            if not data.get("dragging"):
                return
            # Clamp y.
            ny = max(data["y_top"], min(data["y_bot"], event.y))
            frac = 1.0 - (ny - data["y_top"]) / (data["y_bot"] - data["y_top"])
            fill_h = int((data["y_bot"] - data["y_top"]) * (1 - frac))
            fy = data["y_top"] + fill_h

            c.coords(data["fill_id"],
                     data["x"] + data["sw"] // 2 - 2, fy,
                     data["x"] + data["sw"] // 2 + 2, data["y_bot"])
            hy = fy - SLIDER_HANDLE_HEIGHT // 2
            c.coords(data["handle"],
                     data["x"] + 2, hy,
                     data["x"] + data["sw"] - 2, hy + SLIDER_HANDLE_HEIGHT)

            # Update grip lines.
            c.delete(f"slider_grip_{data['name']}")
            for dy in range(-2, 4, 2):
                c.create_line(
                    data["x"] + 6, hy + SLIDER_HANDLE_HEIGHT // 2 + dy,
                    data["x"] + data["sw"] - 6, hy + SLIDER_HANDLE_HEIGHT // 2 + dy,
                    fill=BUTTON_TEXT, width=1,
                    tags=f"slider_grip_{data['name']}",
                )

            if data["name"] == "volume":
                self._volume = frac
            if self._on_param_change:
                self._on_param_change(data["name"], frac)

        def on_release(event, data=slider_data):
            data["dragging"] = False

        c.tag_bind(handle, "<ButtonPress-1>", on_press)
        c.tag_bind(handle, "<B1-Motion>", on_drag)
        c.tag_bind(handle, "<ButtonRelease-1>", on_release)

    # ------------------------------------------------------------------
    # Preset management
    # ------------------------------------------------------------------

    def _select_preset(self, index: int) -> None:
        """Handle preset button click."""
        old = self._current_preset
        self._current_preset = index
        self._highlight_preset(index, old)
        # Update 7-segment display.
        self.set_patch_number(index + 1)
        if self._on_preset_change:
            self._on_preset_change(index)

    def _highlight_preset(self, new: int, old: int | None = None) -> None:
        """Visually highlight the selected preset button."""
        if old is not None and 0 <= old < len(self._preset_buttons):
            self._preset_buttons[old].set_color(BUTTON_COLOR, BUTTON_ACTIVE)
        if 0 <= new < len(self._preset_buttons):
            self._preset_buttons[new].set_color(ACCENT_ORANGE, ACCENT_ORANGE_ACTIVE)

    def navigate_preset(self, delta: int) -> None:
        """Move to the next/previous preset (wraps around).

        Parameters
        ----------
        delta : int
            +1 for next, -1 for previous.
        """
        new_index = (self._current_preset + delta) % 32
        self._select_preset(new_index)

    # ==================================================================
    # Piano keyboard + Wheels
    # ==================================================================

    def _build_keyboard(self) -> None:
        """Build the piano keyboard with pitch bend and mod wheels to the left."""
        self._kb_canvas = tk.Canvas(
            self, width=WINDOW_WIDTH, height=KEYBOARD_HEIGHT,
            bg=PANEL_COLOR, highlightthickness=0,
        )
        self._kb_canvas.pack(fill="x", side="bottom")

        # Draw a thin border line at the top of the keyboard area.
        self._kb_canvas.create_line(
            0, 0, WINDOW_WIDTH, 0, fill=BORDER_COLOR, width=2,
        )

        # Build the wheels on the left side.
        self._build_wheels()

        # Build the piano keys to the right of the wheels.
        self._build_piano_keys()

    # ------------------------------------------------------------------
    # Wheels (Pitch Bend + Mod)
    # ------------------------------------------------------------------

    def _build_wheels(self) -> None:
        """Draw pitch bend and modulation wheels on the left side of the keyboard."""
        c = self._kb_canvas

        # Wheel area background.
        _rounded_rect(
            c, 4, 4, WHEEL_AREA_WIDTH - 4, KEYBOARD_HEIGHT - 4,
            radius=4, fill=GROUP_BG, outline=BORDER_COLOR,
        )

        # --- Pitch Bend Wheel ---
        pb_x = 10
        pb_y = 14
        pb_w = 24
        pb_h = 42
        track_h = pb_h

        # Label.
        c.create_text(
            pb_x + pb_w // 2, pb_y - 4,
            text="PITCH", font=("Helvetica", 6, "bold"),
            fill=LABEL_COLOR, anchor="s",
        )

        # Track (groove).
        c.create_rectangle(
            pb_x + pb_w // 2 - 3, pb_y,
            pb_x + pb_w // 2 + 3, pb_y + track_h,
            fill=WHEEL_TRACK, outline=BORDER_COLOR,
        )

        # Center line marker.
        center_y = pb_y + track_h // 2
        c.create_line(
            pb_x + 2, center_y, pb_x + pb_w - 2, center_y,
            fill=BORDER_COLOR, width=1, dash=(2, 2),
        )

        # Wheel handle (starts at center for pitch bend).
        handle_h = 12
        handle_init_y = center_y - handle_h // 2
        self._pb_handle = _rounded_rect(
            c,
            pb_x + 2, handle_init_y,
            pb_x + pb_w - 2, handle_init_y + handle_h,
            radius=3, fill=WHEEL_COLOR, outline=WHEEL_HIGHLIGHT,
        )
        # Grip line on handle.
        self._pb_grip = c.create_line(
            pb_x + 6, handle_init_y + handle_h // 2,
            pb_x + pb_w - 6, handle_init_y + handle_h // 2,
            fill=WHEEL_HIGHLIGHT, width=1,
        )

        # Pitch bend drag data.
        self._pb_data = {
            "x": pb_x, "w": pb_w, "y_top": pb_y, "y_bot": pb_y + track_h,
            "handle_h": handle_h, "center_y": center_y,
            "dragging": False, "spring_back": True,
            "current_y": handle_init_y,  # track handle top-y for move()
        }

        # Bind pitch bend events.
        c.tag_bind(self._pb_handle, "<ButtonPress-1>", self._pb_press)
        c.tag_bind(self._pb_handle, "<B1-Motion>", self._pb_drag)
        c.tag_bind(self._pb_handle, "<ButtonRelease-1>", self._pb_release)
        c.tag_bind(self._pb_grip, "<ButtonPress-1>", self._pb_press)
        c.tag_bind(self._pb_grip, "<B1-Motion>", self._pb_drag)
        c.tag_bind(self._pb_grip, "<ButtonRelease-1>", self._pb_release)

        # --- Modulation Wheel ---
        mod_x = 46
        mod_y = 14
        mod_w = 24
        mod_h = 42
        mod_track_h = mod_h

        # Label.
        c.create_text(
            mod_x + mod_w // 2, mod_y - 4,
            text="MOD", font=("Helvetica", 6, "bold"),
            fill=LABEL_COLOR, anchor="s",
        )

        # Track (groove).
        c.create_rectangle(
            mod_x + mod_w // 2 - 3, mod_y,
            mod_x + mod_w // 2 + 3, mod_y + mod_track_h,
            fill=WHEEL_TRACK, outline=BORDER_COLOR,
        )

        # Wheel handle (starts at bottom for mod wheel).
        mod_handle_h = 12
        mod_handle_init_y = mod_y + mod_track_h - mod_handle_h
        self._mod_handle = _rounded_rect(
            c,
            mod_x + 2, mod_handle_init_y,
            mod_x + mod_w - 2, mod_handle_init_y + mod_handle_h,
            radius=3, fill=WHEEL_COLOR, outline=WHEEL_HIGHLIGHT,
        )
        # Grip line.
        self._mod_grip = c.create_line(
            mod_x + 6, mod_handle_init_y + mod_handle_h // 2,
            mod_x + mod_w - 6, mod_handle_init_y + mod_handle_h // 2,
            fill=WHEEL_HIGHLIGHT, width=1,
        )

        # Mod wheel drag data.
        self._mod_data = {
            "x": mod_x, "w": mod_w, "y_top": mod_y, "y_bot": mod_y + mod_track_h,
            "handle_h": mod_handle_h,
            "dragging": False, "spring_back": False,
            "current_y": mod_handle_init_y,  # track handle top-y for move()
        }

        # Bind mod wheel events.
        c.tag_bind(self._mod_handle, "<ButtonPress-1>", self._mod_press)
        c.tag_bind(self._mod_handle, "<B1-Motion>", self._mod_drag)
        c.tag_bind(self._mod_handle, "<ButtonRelease-1>", self._mod_release)
        c.tag_bind(self._mod_grip, "<ButtonPress-1>", self._mod_press)
        c.tag_bind(self._mod_grip, "<B1-Motion>", self._mod_drag)
        c.tag_bind(self._mod_grip, "<ButtonRelease-1>", self._mod_release)

        # ---- Additional visual: scale markings on wheels ----
        # Pitch bend scale marks.
        for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
            mark_y = pb_y + int(track_h * frac)
            c.create_line(
                pb_x, mark_y, pb_x + 2, mark_y,
                fill=LABEL_COLOR, width=1,
            )

        # Mod wheel scale marks.
        for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
            mark_y = mod_y + int(mod_track_h * frac)
            c.create_line(
                mod_x, mark_y, mod_x + 2, mark_y,
                fill=LABEL_COLOR, width=1,
            )

        # ---- Labels below wheels ----
        c.create_text(
            WHEEL_AREA_WIDTH // 2, KEYBOARD_HEIGHT - 8,
            text="WHEELS", font=("Helvetica", 6),
            fill=LABEL_COLOR, anchor="s",
        )

    def _pb_press(self, _event: tk.Event) -> None:
        self._pb_data["dragging"] = True

    def _pb_drag(self, event: tk.Event) -> None:
        if not self._pb_data["dragging"]:
            return
        data = self._pb_data
        c = self._kb_canvas
        hh = data["handle_h"]
        ny = max(data["y_top"], min(data["y_bot"] - hh, event.y - hh // 2))

        # Move handle and grip by delta (preserves the rounded polygon shape).
        dy = ny - data["current_y"]
        if dy != 0:
            c.move(self._pb_handle, 0, dy)
            c.move(self._pb_grip, 0, dy)
            data["current_y"] = ny

        # Calculate pitch bend value (0.0=bottom, 1.0=top, 0.5=center).
        total_range = data["y_bot"] - hh - data["y_top"]
        if total_range > 0:
            self._pitch_bend = 1.0 - (ny - data["y_top"]) / total_range
        if self._on_param_change:
            self._on_param_change("pitch_bend", self._pitch_bend)

    def _pb_release(self, _event: tk.Event) -> None:
        self._pb_data["dragging"] = False
        if self._pb_data["spring_back"]:
            # Spring back to center.
            data = self._pb_data
            c = self._kb_canvas
            hh = data["handle_h"]
            target_y = data["center_y"] - hh // 2

            dy = target_y - data["current_y"]
            if dy != 0:
                c.move(self._pb_handle, 0, dy)
                c.move(self._pb_grip, 0, dy)
                data["current_y"] = target_y

            self._pitch_bend = 0.5
            if self._on_param_change:
                self._on_param_change("pitch_bend", 0.5)

    def _mod_press(self, _event: tk.Event) -> None:
        self._mod_data["dragging"] = True

    def _mod_drag(self, event: tk.Event) -> None:
        if not self._mod_data["dragging"]:
            return
        data = self._mod_data
        c = self._kb_canvas
        hh = data["handle_h"]
        ny = max(data["y_top"], min(data["y_bot"] - hh, event.y - hh // 2))

        # Move handle and grip by delta (preserves the rounded polygon shape).
        dy = ny - data["current_y"]
        if dy != 0:
            c.move(self._mod_handle, 0, dy)
            c.move(self._mod_grip, 0, dy)
            data["current_y"] = ny

        # Calculate mod value (0.0=bottom, 1.0=top).
        total_range = data["y_bot"] - hh - data["y_top"]
        if total_range > 0:
            self._mod_wheel = 1.0 - (ny - data["y_top"]) / total_range
        if self._on_param_change:
            self._on_param_change("mod_wheel", self._mod_wheel)

    def _mod_release(self, _event: tk.Event) -> None:
        self._mod_data["dragging"] = False
        # Mod wheel does NOT spring back -- stays where you leave it.

    # ------------------------------------------------------------------
    # Piano keys
    # ------------------------------------------------------------------

    def _build_piano_keys(self) -> None:
        """Build the 5-octave clickable piano keyboard (C1-C6 = MIDI 36-96)."""
        c = self._kb_canvas

        # The keyboard spans C1 (MIDI 36) to C6 (MIDI 96) = 5 octaves + 1.
        self._midi_start = 36  # C1 (MIDI 36)
        self._midi_end = 96    # C6 (MIDI 96)

        # Map MIDI note -> is_black.
        self._black_pattern = {1, 3, 6, 8, 10}

        # Determine white keys in range.
        white_notes: list[int] = []
        black_notes: list[int] = []
        for midi_note in range(self._midi_start, self._midi_end + 1):
            if (midi_note % 12) in self._black_pattern:
                black_notes.append(midi_note)
            else:
                white_notes.append(midi_note)

        self._white_notes = white_notes
        self._black_notes = black_notes

        num_white = len(white_notes)
        kw = WHITE_KEY_WIDTH
        kh = WHITE_KEY_HEIGHT

        # Offset keyboard to the right of the wheel area.
        total_kb_width = num_white * kw
        available_width = WINDOW_WIDTH - WHEEL_AREA_WIDTH
        x_offset = WHEEL_AREA_WIDTH + (available_width - total_kb_width) // 2
        y_offset = 4

        # Draw white keys first.
        self._key_rects: dict[int, int] = {}
        self._key_colors: dict[int, str] = {}

        for i, note in enumerate(white_notes):
            x0 = x_offset + i * kw
            y0 = y_offset
            x1 = x0 + kw - 1
            y1 = y0 + kh

            rect = c.create_rectangle(
                x0, y0, x1, y1,
                fill=WHITE_KEY, outline=KEY_BORDER, width=1,
            )
            self._key_rects[note] = rect
            self._key_colors[note] = WHITE_KEY

            # Note name label at bottom of key (C notes only).
            white_idx = [0, 2, 4, 5, 7, 9, 11]
            semi = note % 12
            if semi == 0:  # C note
                octave = (note // 12) - 1
                c.create_text(
                    x0 + kw // 2, y1 - 10,
                    text=f"C{octave}", font=KEY_LABEL_FONT,
                    fill="#999999",
                )

        # Draw black keys on top.
        white_midi = {n: i for i, n in enumerate(white_notes)}

        black_to_left_white = {
            1: 0, 3: 2, 6: 5, 8: 7, 10: 9,
        }

        bkw = BLACK_KEY_WIDTH
        bkh = BLACK_KEY_HEIGHT

        for note in black_notes:
            semi = note % 12
            left_white_semi = black_to_left_white[semi]
            left_white_note = (note // 12) * 12 + left_white_semi
            if left_white_note not in white_midi:
                continue
            wi = white_midi[left_white_note]
            cx = x_offset + (wi + 1) * kw
            x0 = cx - bkw // 2
            y0 = y_offset
            x1 = x0 + bkw
            y1 = y0 + bkh

            rect = c.create_rectangle(
                x0, y0, x1, y1,
                fill=BLACK_KEY, outline="#000000", width=1,
            )
            # Subtle highlight at top of black key.
            c.create_line(
                x0 + 2, y0 + 2, x1 - 2, y0 + 2,
                fill="#3A3530", width=1,
            )
            self._key_rects[note] = rect
            self._key_colors[note] = BLACK_KEY

        # Bind mouse events for all keys.
        for note, rect in self._key_rects.items():
            c.tag_bind(
                rect, "<ButtonPress-1>",
                lambda e, n=note: self._key_press(n),
            )
            c.tag_bind(
                rect, "<ButtonRelease-1>",
                lambda e, n=note: self._key_release(n),
            )

        # Also handle mouse leaving the keyboard while pressed.
        c.bind("<ButtonRelease-1>", self._key_release_all)

    def _key_press(self, note: int) -> None:
        """Handle mouse-down on a piano key."""
        if note in self._pressed_keys:
            return
        self._pressed_keys.add(note)

        # Visual depress.
        is_black = (note % 12) in self._black_pattern
        pressed_color = BLACK_KEY_PRESSED if is_black else WHITE_KEY_PRESSED
        if note in self._key_rects:
            self._kb_canvas.itemconfigure(
                self._key_rects[note], fill=pressed_color,
            )

        # Callback.
        velocity = 100
        if self._on_note_on:
            self._on_note_on(note, velocity)

    def _key_release(self, note: int) -> None:
        """Handle mouse-up on a piano key."""
        if note not in self._pressed_keys:
            return
        self._pressed_keys.discard(note)

        # Visual restore.
        if note in self._key_rects and note in self._key_colors:
            self._kb_canvas.itemconfigure(
                self._key_rects[note], fill=self._key_colors[note],
            )

        # Callback.
        if self._on_note_off:
            self._on_note_off(note)

    def _key_release_all(self, _event: tk.Event) -> None:
        """Release all pressed keys (mouse left the keyboard area)."""
        for note in list(self._pressed_keys):
            self._key_release(note)

    # ==================================================================
    # Public API for external updates
    # ==================================================================

    def update_display(self, line1: str, line2: str) -> None:
        """Update both LCD lines."""
        self._lcd.set_line1(line1)
        self._lcd.set_line2(line2)

    def update_display_line2(self, text: str) -> None:
        """Update only the bottom LCD line."""
        self._lcd.set_line2(text)

    def update_preset(self, index: int, name: str) -> None:
        """Update the display to show the selected preset."""
        old = self._current_preset
        self._current_preset = index
        self._highlight_preset(index, old)
        self._lcd.set_patch(index + 1, name)
        # Update 7-segment display.
        self.set_patch_number(index + 1)

    def update_algorithm(self, algo_num: int) -> None:
        """Redraw the algorithm display."""
        self.draw_algorithm(algo_num)

    def set_operator_state(self, op_index: int, enabled: bool) -> None:
        """Set a specific operator on/off (0-indexed)."""
        if 0 <= op_index < 6:
            self._operator_states[op_index] = enabled
            led_color = LED_ON if enabled else LED_OFF
            glow = LED_GLOW if enabled else LED_OFF
            self._main_canvas.itemconfigure(
                self._op_leds[op_index], fill=led_color, outline=glow,
            )
            self._op_buttons[op_index].state = enabled
            self.draw_algorithm(self._current_algo)

    def get_volume(self) -> float:
        """Return the current master volume (0.0 - 1.0)."""
        return self._volume

    @property
    def lcd(self) -> LCDDisplay:
        """Direct access to the LCD widget."""
        return self._lcd
