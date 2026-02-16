"""VX7 LCD Display widget.

Emulates the DX7's 2-line, 16-character backlit LCD with the classic
green-on-dark appearance.  Implemented as a Canvas-based widget with
glow effects, scanlines, and a beveled dark bezel.
"""

from __future__ import annotations

import tkinter as tk
from typing import Optional

from .styles import (
    LCD_BG, LCD_TEXT, LCD_DIM, LCD_GLOW,
    LCD_BORDER_OUTER, LCD_BORDER_INNER,
    LCD_FONT, LCD_FONT_SMALL,
    LCD_WIDTH, LCD_HEIGHT, LCD_BEZEL,
    LCD_CHAR_WIDTH, LCD_LINES,
    PANEL_COLOR,
)


class LCDDisplay(tk.Canvas):
    """Canvas-based LCD display emulating the DX7 two-line screen.

    Parameters
    ----------
    parent : tk.Widget
        Parent widget.
    width : int
        Display width in pixels (default from styles).
    height : int
        Display height in pixels (default from styles).
    """

    def __init__(
        self,
        parent: tk.Widget,
        width: int = LCD_WIDTH,
        height: int = LCD_HEIGHT,
        **kwargs,
    ) -> None:
        # Total size includes the bezel border.
        total_w = width + LCD_BEZEL * 2
        total_h = height + LCD_BEZEL * 2

        super().__init__(
            parent,
            width=total_w,
            height=total_h,
            bg=PANEL_COLOR,
            highlightthickness=0,
            **kwargs,
        )

        self._width = width
        self._height = height
        self._bezel = LCD_BEZEL
        self._total_w = total_w
        self._total_h = total_h

        # Current text content.
        self._line1: str = ""
        self._line2: str = ""

        # Canvas item IDs (populated on first draw).
        self._ids_bezel: list[int] = []
        self._ids_scanlines: list[int] = []
        self._id_glow1: int = 0
        self._id_text1: int = 0
        self._id_glow2: int = 0
        self._id_text2: int = 0
        self._ids_grid: list[int] = []

        self._draw_bezel()
        self._draw_lcd_background()
        self._draw_scanlines()
        self._draw_pixel_grid()
        self._create_text_layers()

    # ------------------------------------------------------------------
    # Bezel
    # ------------------------------------------------------------------

    def _draw_bezel(self) -> None:
        """Draw a beveled dark border around the LCD opening."""
        b = self._bezel
        w = self._total_w
        h = self._total_h

        # Outer bevel -- top-left highlight, bottom-right shadow (inset look).
        # Top edge.
        self._ids_bezel.append(
            self.create_line(0, 0, w, 0, fill="#0A0A0A", width=1)
        )
        # Left edge.
        self._ids_bezel.append(
            self.create_line(0, 0, 0, h, fill="#0A0A0A", width=1)
        )
        # Bottom edge (lighter -- light comes from top).
        self._ids_bezel.append(
            self.create_line(0, h - 1, w, h - 1, fill="#2A2A2A", width=1)
        )
        # Right edge.
        self._ids_bezel.append(
            self.create_line(w - 1, 0, w - 1, h, fill="#2A2A2A", width=1)
        )

        # Inner bevel.
        self._ids_bezel.append(
            self.create_line(b - 2, b - 2, w - b + 2, b - 2,
                             fill="#050505", width=1)
        )
        self._ids_bezel.append(
            self.create_line(b - 2, b - 2, b - 2, h - b + 2,
                             fill="#050505", width=1)
        )
        self._ids_bezel.append(
            self.create_line(b - 2, h - b + 1, w - b + 2, h - b + 1,
                             fill="#1E1E1E", width=1)
        )
        self._ids_bezel.append(
            self.create_line(w - b + 1, b - 2, w - b + 1, h - b + 2,
                             fill="#1E1E1E", width=1)
        )

        # Bezel face (dark frame).
        self.create_rectangle(
            1, 1, w - 2, h - 2,
            outline=LCD_BORDER_OUTER, width=1,
        )
        self.create_rectangle(
            b - 1, b - 1, w - b + 1, h - b + 1,
            outline=LCD_BORDER_INNER, width=1,
        )

    # ------------------------------------------------------------------
    # LCD background
    # ------------------------------------------------------------------

    def _draw_lcd_background(self) -> None:
        """Fill the LCD area with the dark green background."""
        b = self._bezel
        self.create_rectangle(
            b, b,
            b + self._width, b + self._height,
            fill=LCD_BG, outline="",
        )

    # ------------------------------------------------------------------
    # Scanline effect
    # ------------------------------------------------------------------

    def _draw_scanlines(self) -> None:
        """Draw subtle horizontal scanlines across the LCD area."""
        b = self._bezel
        x0 = b
        x1 = b + self._width
        for y in range(b, b + self._height, 3):
            sid = self.create_line(
                x0, y, x1, y,
                fill="#061206", width=1, stipple="gray12",
            )
            self._ids_scanlines.append(sid)

    # ------------------------------------------------------------------
    # Pixel grid overlay
    # ------------------------------------------------------------------

    def _draw_pixel_grid(self) -> None:
        """Draw a faint pixel-grid overlay for an authentic LCD look."""
        b = self._bezel
        x0 = b
        y0 = b
        x1 = b + self._width
        y1 = b + self._height

        # Vertical grid lines.
        step = 4
        for x in range(x0, x1, step):
            gid = self.create_line(
                x, y0, x, y1,
                fill="#0D1F0D", width=1, stipple="gray12",
            )
            self._ids_grid.append(gid)

        # Horizontal grid lines.
        for y in range(y0, y1, step):
            gid = self.create_line(
                x0, y, x1, y,
                fill="#0D1F0D", width=1, stipple="gray12",
            )
            self._ids_grid.append(gid)

    # ------------------------------------------------------------------
    # Text layers (glow + crisp text for each line)
    # ------------------------------------------------------------------

    def _create_text_layers(self) -> None:
        """Create canvas text items for the two LCD lines with glow."""
        b = self._bezel
        cx = b + self._width // 2
        line_height = self._height // 2

        # Line 1 -- upper half.
        y1 = b + line_height // 2 + 2

        # Glow layer (slightly larger, blurred look via stipple).
        self._id_glow1 = self.create_text(
            cx, y1,
            text="",
            font=LCD_FONT,
            fill=LCD_GLOW,
            anchor="center",
            stipple="gray50",
        )
        # Crisp text on top.
        self._id_text1 = self.create_text(
            cx, y1,
            text="",
            font=LCD_FONT,
            fill=LCD_TEXT,
            anchor="center",
        )

        # Line 2 -- lower half.
        y2 = b + line_height + line_height // 2 - 2

        self._id_glow2 = self.create_text(
            cx, y2,
            text="",
            font=LCD_FONT_SMALL,
            fill=LCD_GLOW,
            anchor="center",
            stipple="gray50",
        )
        self._id_text2 = self.create_text(
            cx, y2,
            text="",
            font=LCD_FONT_SMALL,
            fill=LCD_TEXT,
            anchor="center",
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_line1(self, text: str) -> None:
        """Set the top line of the LCD (max 16 characters)."""
        self._line1 = text[:LCD_CHAR_WIDTH].ljust(LCD_CHAR_WIDTH)
        self.itemconfigure(self._id_text1, text=self._line1)
        self.itemconfigure(self._id_glow1, text=self._line1)

    def set_line2(self, text: str) -> None:
        """Set the bottom line of the LCD (max 16 characters)."""
        self._line2 = text[:LCD_CHAR_WIDTH].ljust(LCD_CHAR_WIDTH)
        self.itemconfigure(self._id_text2, text=self._line2)
        self.itemconfigure(self._id_glow2, text=self._line2)

    def set_patch(self, number: int, name: str) -> None:
        """Convenience: set line 1 to a formatted patch display.

        Shows the patch number right-justified in a 2-digit field,
        followed by the patch name, e.g. " 1 E.PIANO 1   ".
        """
        num_str = f"{number:>2d}"
        # Remaining space for name: 16 - 2 (number) - 1 (space) = 13 chars
        name_str = name[:13].ljust(13)
        self.set_line1(f"{num_str} {name_str}")

    def clear(self) -> None:
        """Clear both lines."""
        self.set_line1("")
        self.set_line2("")

    def flash(self, duration_ms: int = 120) -> None:
        """Briefly invert the LCD colors for a visual flash effect."""
        self.itemconfigure(self._id_text1, fill=LCD_BG)
        self.itemconfigure(self._id_text2, fill=LCD_BG)
        self.itemconfigure(self._id_glow1, fill=LCD_BG)
        self.itemconfigure(self._id_glow2, fill=LCD_BG)

        # Change background to bright.
        b = self._bezel
        self._flash_rect = self.create_rectangle(
            b, b, b + self._width, b + self._height,
            fill=LCD_TEXT, outline="",
        )
        # Move text above the flash rect.
        self.tag_raise(self._id_text1)
        self.tag_raise(self._id_text2)

        self.after(duration_ms, self._unflash)

    def _unflash(self) -> None:
        """Restore normal LCD colors after a flash."""
        if hasattr(self, "_flash_rect"):
            self.delete(self._flash_rect)
            del self._flash_rect
        self.itemconfigure(self._id_text1, fill=LCD_TEXT)
        self.itemconfigure(self._id_text2, fill=LCD_TEXT)
        self.itemconfigure(self._id_glow1, fill=LCD_GLOW)
        self.itemconfigure(self._id_glow2, fill=LCD_GLOW)
