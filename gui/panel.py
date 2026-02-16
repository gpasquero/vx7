"""VX7 main control panel.

Replicates the Yamaha DX7 Mk1 front-panel layout using tkinter Canvas widgets.
The panel is arranged in horizontal sections from left to right, matching the
real DX7 hardware:

    DATA ENTRY | LCD + MEMORY | EDIT/OPERATORS | ALGORITHM + PARAMS | MASTER

- Silver header strip with VX7 branding
- LCD display with green-on-dark text
- Algorithm topology diagram
- Operator on/off toggles with LED indicators
- Parameter editing buttons
- Preset/memory selection grid (32 buttons in 2 rows of 16)
- Function buttons (STORE, EDIT, etc.)
- Master volume and tune sliders
- Four-octave clickable piano keyboard (C2-C6)
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
    """Main DX7-style control panel.

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

        Layout is horizontal, left to right:
        DATA ENTRY | LCD + MEMORY | EDIT/OPERATORS | ALGORITHM + PARAMS | MASTER
        """
        main_h = WINDOW_HEIGHT - HEADER_HEIGHT - KEYBOARD_HEIGHT
        self._main_canvas = tk.Canvas(
            self, width=WINDOW_WIDTH, height=main_h,
            bg=BODY_COLOR, highlightthickness=0,
        )
        self._main_canvas.pack(fill="both", side="top")

        # Build each horizontal section.
        self._build_data_entry_section()
        self._build_lcd_and_memory_section()
        self._build_edit_operator_section()
        self._build_algorithm_param_section()
        self._build_master_section()

    # ------------------------------------------------------------------
    # Section 1: DATA ENTRY (far left) -- slider + up/down buttons
    # ------------------------------------------------------------------

    def _build_data_entry_section(self) -> None:
        """Vertical DATA ENTRY slider with YES/NO (up/down) buttons below."""
        sx = 12
        sy = 8

        # Section label.
        self._main_canvas.create_text(
            sx + 22, sy, text="DATA ENTRY", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="n",
        )

        # Background panel.
        panel_w = 50
        panel_h = SLIDER_HEIGHT + 80
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

        # UP arrow button (YES / increment).
        arrow_w = 36
        arrow_h = 28
        arrow_x = sx + (panel_w - arrow_w) // 2
        arrow_y = sy + 24 + SLIDER_HEIGHT + 8

        MembraneButton(
            self._main_canvas,
            arrow_x, arrow_y,
            width=arrow_w, height=arrow_h,
            text="\u25B2", color=ACCENT_BLUE, active_color=ACCENT_BLUE_ACTIVE,
            command=lambda: self.navigate_preset(-1),
            font=("Helvetica", 11, "bold"),
            text_color="#FFFFFF",
        )

        # DOWN arrow button (NO / decrement).
        MembraneButton(
            self._main_canvas,
            arrow_x, arrow_y + arrow_h + 4,
            width=arrow_w, height=arrow_h,
            text="\u25BC", color=ACCENT_BLUE, active_color=ACCENT_BLUE_ACTIVE,
            command=lambda: self.navigate_preset(1),
            font=("Helvetica", 11, "bold"),
            text_color="#FFFFFF",
        )

    # ------------------------------------------------------------------
    # Section 2: LCD + MEMORY SELECT (left-center)
    # ------------------------------------------------------------------

    def _build_lcd_and_memory_section(self) -> None:
        """LCD display at top, 32 preset buttons in 2 rows of 16 below."""
        sx = 72
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

        # MEMORY SELECT label.
        mem_y = sy + 14 + 92 + 8  # Below LCD (LCD is ~92px with bezel)
        self._main_canvas.create_text(
            sx, mem_y, text="MEMORY SELECT", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="nw",
        )

        # 32 preset buttons in 2 rows of 16.
        bs = PRESET_BUTTON_SIZE + 2  # button + gap
        preset_y = mem_y + 14

        # Background panel for presets.
        panel_w = 16 * bs + 8
        panel_h = 2 * bs + 8
        _rounded_rect(
            self._main_canvas,
            sx - 4, preset_y - 4,
            sx + panel_w, preset_y + panel_h,
            radius=4, fill=GROUP_BG, outline=BORDER_COLOR,
        )

        self._preset_buttons: list[MembraneButton] = []
        for i in range(32):
            col = i % 16
            row = i // 16
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
    # Section 3: EDIT / FUNCTION + OPERATORS (center)
    # ------------------------------------------------------------------

    def _build_edit_operator_section(self) -> None:
        """Function buttons (STORE, EDIT, COMPARE) at top, operator toggles below."""
        sx = 564
        sy = 8

        # --- FUNCTION BUTTONS ---
        self._main_canvas.create_text(
            sx, sy, text="FUNCTION", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="nw",
        )

        func_names = [
            "STORE", "EDIT", "COMPARE",
        ]

        bw = MEMBRANE_BUTTON_WIDTH + 2
        bh = MEMBRANE_BUTTON_HEIGHT + 2
        func_y = sy + 14

        # Background panel for function buttons.
        func_panel_w = 3 * bw + 8
        func_panel_h = bh + 8
        _rounded_rect(
            self._main_canvas,
            sx - 4, func_y - 4,
            sx + func_panel_w, func_y + func_panel_h,
            radius=4, fill=GROUP_BG, outline=BORDER_COLOR,
        )

        self._func_buttons: list[MembraneButton] = []
        for i, name in enumerate(func_names):
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

        # --- OPERATOR SELECT ---
        op_y = func_y + func_panel_h + 20
        self._main_canvas.create_text(
            sx, op_y, text="OPERATOR SELECT", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="nw",
        )

        op_btn_y = op_y + 14

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

        # --- Additional function row below operators: ALGO+, ALGO-, INIT ---
        extra_y = op_btn_y + op_panel_h + 12

        extra_names = ["ALGO+", "ALGO-", "INIT"]

        extra_panel_w = 3 * bw + 8
        extra_panel_h = bh + 8
        _rounded_rect(
            self._main_canvas,
            sx - 4, extra_y - 4,
            sx + extra_panel_w, extra_y + extra_panel_h,
            radius=4, fill=GROUP_BG, outline=BORDER_COLOR,
        )

        for i, name in enumerate(extra_names):
            bx = sx + i * bw + 4
            by = extra_y + 4

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
    # Section 4: ALGORITHM + PARAMETERS (right)
    # ------------------------------------------------------------------

    def _build_algorithm_param_section(self) -> None:
        """Algorithm display at top, parameter editing buttons below."""
        sx = 760
        sy = 8

        # --- ALGORITHM DISPLAY ---
        self._main_canvas.create_text(
            sx, sy, text="ALGORITHM", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="nw",
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

        # Algorithm number label.
        self._algo_num_label = self._algo_canvas.create_text(
            ALGO_DISPLAY_WIDTH - 6, 8,
            text="1", font=("Courier", 14, "bold"),
            fill=LCD_TEXT, anchor="ne",
        )

        self.draw_algorithm(1)

        # --- PARAMETER BUTTONS ---
        param_y = sy + 14 + ALGO_DISPLAY_HEIGHT + 12
        self._main_canvas.create_text(
            sx, param_y, text="PARAMETERS", font=SECTION_FONT,
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

        param_btn_y = param_y + 14
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

        # Update the algorithm number.
        c.itemconfigure(self._algo_num_label, text=str(algo_num))
        c.tag_raise(self._algo_num_label)

    # ------------------------------------------------------------------
    # Section 5: MASTER (far right) -- volume + tune sliders
    # ------------------------------------------------------------------

    def _build_master_section(self) -> None:
        """Volume slider and master tune slider on the far right."""
        sx = 960
        sy = 8

        self._main_canvas.create_text(
            sx + 100, sy, text="MASTER", font=SECTION_FONT,
            fill=SECTION_LABEL_COLOR, anchor="n",
        )

        panel_w = 200
        panel_h = SLIDER_HEIGHT + 50
        _rounded_rect(
            self._main_canvas,
            sx, sy + 14,
            sx + panel_w, sy + 14 + panel_h,
            radius=4, fill=GROUP_BG, outline=BORDER_COLOR,
        )

        # Volume slider.
        vol_x = sx + 40
        self._main_canvas.create_text(
            vol_x + SLIDER_WIDTH // 2, sy + 28,
            text="VOLUME", font=LABEL_FONT_BOLD,
            fill=LABEL_COLOR, anchor="n",
        )
        self._build_slider(vol_x, sy + 42, "volume", self._volume)

        # Tune slider.
        tune_x = sx + 130
        self._main_canvas.create_text(
            tune_x + SLIDER_WIDTH // 2, sy + 28,
            text="TUNE", font=LABEL_FONT_BOLD,
            fill=LABEL_COLOR, anchor="n",
        )
        self._build_slider(tune_x, sy + 42, "tune", 0.5)

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
    # Piano keyboard
    # ==================================================================

    def _build_keyboard(self) -> None:
        """Build the 4-octave clickable piano keyboard (C2-C6 = MIDI 36-96)."""
        self._kb_canvas = tk.Canvas(
            self, width=WINDOW_WIDTH, height=KEYBOARD_HEIGHT,
            bg=PANEL_COLOR, highlightthickness=0,
        )
        self._kb_canvas.pack(fill="x", side="bottom")

        # Draw a thin border line at the top of the keyboard area.
        self._kb_canvas.create_line(
            0, 0, WINDOW_WIDTH, 0, fill=BORDER_COLOR, width=2,
        )

        # The keyboard spans C2 (MIDI 36) to C6 (MIDI 96) = 4 octaves + 1.
        self._midi_start = 36  # C2
        self._midi_end = 96    # C6

        # Map MIDI note -> is_black.
        # Pattern in one octave: W B W B W W B W B W B W
        #                        C C#D D#E F F#G G#A A#B
        self._black_pattern = {1, 3, 6, 8, 10}  # semitone offsets for black keys

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

        # Center the keyboard.
        total_kb_width = num_white * kw
        x_offset = (WINDOW_WIDTH - total_kb_width) // 2
        y_offset = 4

        # Draw white keys first.
        self._key_rects: dict[int, int] = {}  # midi_note -> canvas rect id
        self._key_colors: dict[int, str] = {}

        for i, note in enumerate(white_notes):
            x0 = x_offset + i * kw
            y0 = y_offset
            x1 = x0 + kw - 1
            y1 = y0 + kh

            rect = self._kb_canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=WHITE_KEY, outline=KEY_BORDER, width=1,
            )
            self._key_rects[note] = rect
            self._key_colors[note] = WHITE_KEY

            # Note name label at bottom of key.
            note_names = ["C", "D", "E", "F", "G", "A", "B"]
            white_idx = [0, 2, 4, 5, 7, 9, 11]
            semi = note % 12
            if semi in white_idx:
                nname = note_names[white_idx.index(semi)]
                octave = (note // 12) - 1
                if nname == "C":
                    self._kb_canvas.create_text(
                        x0 + kw // 2, y1 - 10,
                        text=f"C{octave}", font=KEY_LABEL_FONT,
                        fill="#999999",
                    )

        # Draw black keys on top.
        # Black key positions relative to the white key they sit between.
        # C#: between C and D, D#: between D and E, F#: between F and G,
        # G#: between G and A, A#: between A and B.
        # We compute the x position based on the white key index.
        white_midi = {n: i for i, n in enumerate(white_notes)}

        # For each black key, find which white key is just below it.
        black_to_left_white = {
            1: 0, 3: 2, 6: 5, 8: 7, 10: 9,
        }  # black semitone -> white semitone to its left

        bkw = BLACK_KEY_WIDTH
        bkh = BLACK_KEY_HEIGHT

        for note in black_notes:
            semi = note % 12
            left_white_semi = black_to_left_white[semi]
            left_white_note = (note // 12) * 12 + left_white_semi
            if left_white_note not in white_midi:
                continue
            wi = white_midi[left_white_note]
            # Black key center is at the right edge of the left white key.
            cx = x_offset + (wi + 1) * kw
            x0 = cx - bkw // 2
            y0 = y_offset
            x1 = x0 + bkw
            y1 = y0 + bkh

            rect = self._kb_canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=BLACK_KEY, outline="#000000", width=1,
            )
            # Subtle highlight at top of black key.
            self._kb_canvas.create_line(
                x0 + 2, y0 + 2, x1 - 2, y0 + 2,
                fill="#3A3530", width=1,
            )
            self._key_rects[note] = rect
            self._key_colors[note] = BLACK_KEY

        # Bind mouse events for all keys.
        for note, rect in self._key_rects.items():
            self._kb_canvas.tag_bind(
                rect, "<ButtonPress-1>",
                lambda e, n=note: self._key_press(n),
            )
            self._kb_canvas.tag_bind(
                rect, "<ButtonRelease-1>",
                lambda e, n=note: self._key_release(n),
            )

        # Also handle mouse leaving the keyboard while pressed.
        self._kb_canvas.bind("<ButtonRelease-1>", self._key_release_all)

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
