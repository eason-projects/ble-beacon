import wx
from datetime import datetime

class ColorPanel(wx.Panel):
    """A panel with a solid background color based on RSSI value."""
    
    def __init__(self, parent, *args, **kwargs):
        super(ColorPanel, self).__init__(parent, *args, **kwargs)
        
        self.background_color = wx.Colour(0, 0, 0)  # Default black
        
        # Bind the paint event
        self.Bind(wx.EVT_PAINT, self.on_paint)
    
    def set_background_color(self, color):
        """Set the background color."""
        self.background_color = color
        self.Refresh()  # Force a redraw
    
    def on_paint(self, event):
        """Draw the background with a solid color."""
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        
        if not gc:
            event.Skip()
            return
            
        width, height = self.GetSize()
        
        # Fill the background with the solid color
        gc.SetBrush(wx.Brush(self.background_color))
        gc.DrawRectangle(0, 0, width, height)

class RSSIDisplayFrame(wx.Frame):
    """A frame to display RSSI and last seen time in large text."""
    
    def __init__(self, parent, title="RSSI Display"):
        super(RSSIDisplayFrame, self).__init__(parent, title=title, size=(400, 300),
                                              style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        
        self.parent = parent
        self.is_fullscreen = False
        self.selected_key = None
        self.current_rssi = None  # Track current RSSI value
        
        # For smooth color transitions
        self.target_color = wx.Colour(0, 0, 0)  # Target color to transition to
        self.current_color = wx.Colour(0, 0, 0)  # Current displayed color
        self.color_transition_steps = 10  # Number of steps for color transition
        self.color_transition_current_step = 0  # Current step in the transition
        
        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Device selection
        device_sizer = wx.BoxSizer(wx.HORIZONTAL)
        device_label = wx.StaticText(self.panel, label="Select Device:")
        self.device_choice = wx.Choice(self.panel, choices=[])
        device_sizer.Add(device_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        device_sizer.Add(self.device_choice, 1, wx.ALL, 5)
        self.main_sizer.Add(device_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Create a fullscreen panel for displaying RSSI in fullscreen mode
        self.fullscreen_panel = ColorPanel(self.panel)
        self.fullscreen_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # RSSI value for fullscreen
        self.fullscreen_rssi = wx.StaticText(self.fullscreen_panel, label="N/A", 
                                            style=wx.ALIGN_CENTER_HORIZONTAL | wx.ST_NO_AUTORESIZE)
        self.fullscreen_rssi.SetForegroundColour(wx.Colour(255, 255, 255))  # White text
        self.fullscreen_rssi.SetFont(wx.Font(120, wx.FONTFAMILY_DEFAULT, 
                                           wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # Last seen value for fullscreen
        self.fullscreen_last_seen = wx.StaticText(self.fullscreen_panel, label="N/A", 
                                                style=wx.ALIGN_CENTER_HORIZONTAL | wx.ST_NO_AUTORESIZE)
        self.fullscreen_last_seen.SetForegroundColour(wx.Colour(255, 255, 255))  # White text
        self.fullscreen_last_seen.SetFont(wx.Font(40, wx.FONTFAMILY_DEFAULT, 
                                               wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # Device name for fullscreen
        self.fullscreen_device_name = wx.StaticText(self.fullscreen_panel, label="No Device Selected", 
                                                  style=wx.ALIGN_CENTER_HORIZONTAL | wx.ST_NO_AUTORESIZE)
        self.fullscreen_device_name.SetForegroundColour(wx.Colour(255, 255, 255))  # White text
        self.fullscreen_device_name.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, 
                                                 wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # Add to fullscreen sizer with spacers to center vertically
        self.fullscreen_sizer.AddStretchSpacer(1)
        
        # Create horizontal sizer for device name
        device_name_h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        device_name_h_sizer.AddStretchSpacer(1)
        device_name_h_sizer.Add(self.fullscreen_device_name, 0, wx.ALIGN_CENTER, 10)
        device_name_h_sizer.AddStretchSpacer(1)
        
        # Add the device name sizer to the main fullscreen sizer
        self.fullscreen_sizer.Add(device_name_h_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        # Create horizontal sizers for each text control to ensure center alignment
        rssi_h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        rssi_h_sizer.AddStretchSpacer(1)
        rssi_h_sizer.Add(self.fullscreen_rssi, 0, wx.ALIGN_CENTER, 10)
        rssi_h_sizer.AddStretchSpacer(1)
        
        last_seen_h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        last_seen_h_sizer.AddStretchSpacer(1)
        last_seen_h_sizer.Add(self.fullscreen_last_seen, 0, wx.ALIGN_CENTER, 10)
        last_seen_h_sizer.AddStretchSpacer(1)
        
        # Add the horizontal sizers to the main fullscreen sizer
        self.fullscreen_sizer.Add(rssi_h_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.fullscreen_sizer.Add(last_seen_h_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        self.fullscreen_sizer.AddStretchSpacer(1)
        
        self.fullscreen_panel.SetSizer(self.fullscreen_sizer)
        self.main_sizer.Add(self.fullscreen_panel, 1, wx.EXPAND)
        self.fullscreen_panel.Hide()  # Hide initially
        
        # RSSI display container (to center the RSSI value) - for normal mode
        rssi_container = wx.BoxSizer(wx.VERTICAL)
        
        # RSSI label
        rssi_label = wx.StaticText(self.panel, label="RSSI:")
        rssi_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        rssi_container.Add(rssi_label, 0, wx.ALIGN_CENTER, 5)
        
        # Create a panel with background color for the RSSI value
        self.rssi_bg_panel = ColorPanel(self.panel)
        self.rssi_bg_panel.set_background_color(wx.Colour(0, 0, 0))  # Black background initially
        
        # Create a sizer for the background panel to center the RSSI value
        rssi_bg_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # RSSI value with centered text
        self.rssi_value = wx.StaticText(self.rssi_bg_panel, label="N/A", 
                                      style=wx.ALIGN_CENTER_HORIZONTAL | wx.ST_NO_AUTORESIZE)
        self.rssi_value.SetFont(wx.Font(60, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.rssi_value.SetForegroundColour(wx.Colour(255, 255, 255))  # White text
        
        # Add the RSSI value to the background panel sizer with centering
        rssi_bg_sizer.AddStretchSpacer(1)
        rssi_bg_sizer.Add(self.rssi_value, 0, wx.ALIGN_CENTER, 10)
        rssi_bg_sizer.AddStretchSpacer(1)
        
        # Set the sizer for the background panel
        self.rssi_bg_panel.SetSizer(rssi_bg_sizer)
        
        # Add the background panel to the RSSI container
        rssi_container.Add(self.rssi_bg_panel, 1, wx.EXPAND, 10)
        
        # Add the RSSI container to the main sizer
        self.main_sizer.Add(rssi_container, 1, wx.EXPAND | wx.ALL, 10)
        
        # Last seen container
        last_seen_container = wx.BoxSizer(wx.VERTICAL)
        
        # Last seen label
        last_seen_label = wx.StaticText(self.panel, label="Last Seen:")
        last_seen_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        last_seen_container.Add(last_seen_label, 0, wx.ALIGN_CENTER, 5)
        
        # Last seen value
        self.last_seen_value = wx.StaticText(self.panel, label="N/A", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.last_seen_value.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        last_seen_container.Add(self.last_seen_value, 0, wx.ALIGN_CENTER, 5)
        
        # Add the last seen container to the main sizer
        self.main_sizer.Add(last_seen_container, 0, wx.EXPAND | wx.ALL, 5)
        
        # Add fullscreen button
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.fullscreen_button = wx.Button(self.panel, label="Toggle Fullscreen")
        self.fullscreen_button.Bind(wx.EVT_BUTTON, self.on_toggle_fullscreen)
        button_sizer.Add(self.fullscreen_button, 0, wx.ALL, 5)
        self.main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        
        # Add fullscreen instructions
        instructions = wx.StaticText(self.panel, label="Press ESC to exit fullscreen mode")
        instructions.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        self.main_sizer.Add(instructions, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 5)
        
        self.panel.SetSizer(self.main_sizer)
        self.Centre()
        
        # Bind device selection event
        self.device_choice.Bind(wx.EVT_CHOICE, self.on_device_selected)
        
        # Bind size event to adjust font size
        self.Bind(wx.EVT_SIZE, self.on_size)
        
        # Bind key events for ESC key to exit fullscreen
        self.panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.rssi_value.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.last_seen_value.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.fullscreen_panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
        # Make the panel and text controls focusable to receive key events
        self.panel.SetFocus()
        self.panel.SetFocusIgnoringChildren()
        
        # Set up a timer to update the display
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_display, self.timer)
        self.timer.Start(500)  # Update every 500ms
        
        # Bind the close event
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        # Initial font size adjustment
        self.adjust_font_size()
    
    def on_key_down(self, event):
        """Handle key press events."""
        key_code = event.GetKeyCode()
        
        # Check for ESC key (27) to exit fullscreen
        if key_code == wx.WXK_ESCAPE and self.is_fullscreen:
            print("ESC key pressed, exiting fullscreen mode")
            self.exit_fullscreen()
        else:
            event.Skip()
    
    def exit_fullscreen(self):
        """Exit fullscreen mode."""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.ShowFullScreen(False)
            
            # Switch from fullscreen panel to normal controls
            self.fullscreen_panel.Hide()
            
            # Show all normal controls
            for child in self.panel.GetChildren():
                if child != self.fullscreen_panel and not child.IsShown():
                    child.Show()
            
            # Adjust the font size for the new window size
            self.adjust_font_size()
            self.panel.Layout()
    
    def on_toggle_fullscreen(self, event):
        """Toggle fullscreen mode."""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.is_fullscreen = True
            
            # Hide normal controls and show fullscreen panel
            for child in self.panel.GetChildren():
                if child != self.fullscreen_panel:
                    child.Hide()
            
            self.fullscreen_panel.Show()
            self.ShowFullScreen(True)
            
            # Update the background color
            self.update_background_color()
            
            # Adjust the font size for the new window size
            self.adjust_font_size()
            self.panel.Layout()
    
    def on_size(self, event):
        """Handle window resize events."""
        event.Skip()  # Process the default behavior first
        self.adjust_font_size()
    
    def adjust_font_size(self):
        """Adjust font size based on window size."""
        # Get the current window size
        window_width, window_height = self.GetClientSize()
        
        if self.is_fullscreen:
            # For fullscreen mode, use the fullscreen panel controls
            # Calculate appropriate font sizes based on window dimensions
            rssi_font_size = max(int(min(window_width, window_height) / 3), 60)
            last_seen_font_size = max(int(rssi_font_size / 3), 20)
            device_name_font_size = max(int(rssi_font_size / 4), 10)
            
            # Update the fonts for fullscreen controls
            self.fullscreen_rssi.SetFont(wx.Font(rssi_font_size, wx.FONTFAMILY_DEFAULT, 
                                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            self.fullscreen_last_seen.SetFont(wx.Font(last_seen_font_size, wx.FONTFAMILY_DEFAULT, 
                                                   wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            self.fullscreen_device_name.SetFont(wx.Font(device_name_font_size, wx.FONTFAMILY_DEFAULT, 
                                                     wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        else:
            # For normal mode, use the regular controls
            # Calculate appropriate font sizes based on window dimensions
            rssi_font_size = max(int(min(window_width, window_height) / 4), 20)
            last_seen_font_size = max(int(rssi_font_size / 2.5), 12)
            
            # Update the fonts for normal controls
            self.rssi_value.SetFont(wx.Font(rssi_font_size, wx.FONTFAMILY_DEFAULT, 
                                         wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            self.last_seen_value.SetFont(wx.Font(last_seen_font_size, wx.FONTFAMILY_DEFAULT, 
                                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # Force a layout update
        self.panel.Layout()
    
    def update_display(self, event):
        """Update the RSSI and last seen display."""
        if self.selected_key and self.selected_key in self.parent.beacon_data:
            data = self.parent.beacon_data[self.selected_key]
            rssi_value = str(data.get('rssi', 'N/A'))
            last_seen_value = data.get('last_seen', 'N/A')
            
            # Create device display name
            device_name = f"{data['type']} - "
            if data['type'] == "iBeacon":
                device_name += f"{data['uuid'][-8:]} ({data['major']}/{data['minor']})"
            else:
                device_name += f"{data.get('id', 'unknown')}"
            
            # Update both normal and fullscreen displays
            self.rssi_value.SetLabel(rssi_value)
            self.last_seen_value.SetLabel(last_seen_value)
            self.fullscreen_rssi.SetLabel(rssi_value)
            self.fullscreen_last_seen.SetLabel(last_seen_value)
            self.fullscreen_device_name.SetLabel(device_name)
            
            # Update the background color based on RSSI value
            try:
                self.current_rssi = int(rssi_value)
                self.update_background_color()
            except (ValueError, TypeError):
                # If RSSI is not a valid number, don't update the color
                pass
        else:
            self.rssi_value.SetLabel("N/A")
            self.last_seen_value.SetLabel("N/A")
            self.fullscreen_rssi.SetLabel("N/A")
            self.fullscreen_last_seen.SetLabel("N/A")
            self.fullscreen_device_name.SetLabel("No Device Selected")
    
    def get_rssi_color(self):
        """Determine the background color based on RSSI value using a continuous color map."""
        if self.current_rssi is None:
            return wx.Colour(0, 0, 0)  # Default black
        
        # RSSI values are negative, typically ranging from -30 (very good) to -100 (very bad)
        # Normalize the RSSI value to a range of 0.0 to 1.0
        # -30 or better -> 1.0 (best)
        # -100 or worse -> 0.0 (worst)
        
        min_rssi = -100  # Worst signal
        max_rssi = -30   # Best signal
        
        # Clamp RSSI value to our range
        clamped_rssi = max(min(self.current_rssi, max_rssi), min_rssi)
        
        # Normalize to 0.0 - 1.0
        normalized = (clamped_rssi - min_rssi) / (max_rssi - min_rssi)
        
        # Use HSV color space for smooth transitions
        # Hue: 0 (red) for worst signal, through yellow, green, cyan, blue, to 240 (purple) for best signal
        # This gives a much smoother transition through the color spectrum
        hue = normalized * 240  # 0 to 240 degrees in HSV (red to purple)
        saturation = 1.0        # Full saturation
        value = 1.0             # Full brightness
        
        # Convert HSV to RGB
        # Algorithm from https://en.wikipedia.org/wiki/HSL_and_HSV#HSV_to_RGB
        c = value * saturation
        x = c * (1 - abs((hue / 60) % 2 - 1))
        m = value - c
        
        if 0 <= hue < 60:
            r, g, b = c, x, 0
        elif 60 <= hue < 120:
            r, g, b = x, c, 0
        elif 120 <= hue < 180:
            r, g, b = 0, c, x
        elif 180 <= hue < 240:
            r, g, b = 0, x, c
        elif 240 <= hue < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        # Convert to 0-255 range
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        
        return wx.Colour(r, g, b)
    
    def update_background_color(self):
        """Update the background color based on the current RSSI value."""
        # Get the target color based on RSSI
        self.target_color = self.get_rssi_color()
        
        # If this is the first update, initialize current_color to target_color
        if self.current_color == wx.Colour(0, 0, 0) and self.target_color != wx.Colour(0, 0, 0):
            self.current_color = self.target_color
        
        # Reset the transition
        self.color_transition_current_step = 0
        
        # Start the color transition timer if not already running
        if not hasattr(self, 'color_timer') or not self.color_timer.IsRunning():
            self.color_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.update_color_transition, self.color_timer)
            self.color_timer.Start(30)  # Update every 30ms for smooth transition
    
    def update_color_transition(self, event):
        """Update the color transition animation."""
        if self.color_transition_current_step >= self.color_transition_steps:
            # Transition complete
            self.color_timer.Stop()
            self.current_color = self.target_color
        else:
            # Calculate interpolated color
            r1, g1, b1 = self.current_color.Red(), self.current_color.Green(), self.current_color.Blue()
            r2, g2, b2 = self.target_color.Red(), self.target_color.Green(), self.target_color.Blue()
            
            progress = (self.color_transition_current_step + 1) / self.color_transition_steps
            
            r = int(r1 + (r2 - r1) * progress)
            g = int(g1 + (g2 - g1) * progress)
            b = int(b1 + (b2 - b1) * progress)
            
            self.current_color = wx.Colour(r, g, b)
            self.color_transition_current_step += 1
        
        # Apply the current color
        if self.is_fullscreen:
            self.fullscreen_panel.set_background_color(self.current_color)
        
        # Always update the RSSI value background color in normal mode
        self.rssi_bg_panel.set_background_color(self.current_color)
    
    def on_close(self, event):
        """Handle the window closing event."""
        # Stop the timer
        if self.timer.IsRunning():
            self.timer.Stop()
        
        # Stop the color transition timer if it's running
        if hasattr(self, 'color_timer') and self.color_timer.IsRunning():
            self.color_timer.Stop()
        
        # Update the parent's reference to this window
        if hasattr(self.parent, 'rssi_display'):
            self.parent.rssi_display = None
        
        # Hide the window instead of destroying it
        self.Hide()
    
    def on_device_selected(self, event):
        """Handle device selection."""
        selection = self.device_choice.GetSelection()
        if selection != wx.NOT_FOUND:
            self.selected_key = self.device_choice.GetClientData(selection)
            self.update_display(None)
    
    def update_device_list(self, beacon_data):
        """Update the device choice control with current beacons."""
        current_selection = self.device_choice.GetSelection()
        selected_key = None
        if current_selection != wx.NOT_FOUND:
            selected_key = self.device_choice.GetClientData(current_selection)
        
        self.device_choice.Clear()
        
        for key, data in beacon_data.items():
            display_name = f"{data['type']} - "
            if data['type'] == "iBeacon":
                display_name += f"{data['uuid'][-8:]} ({data['major']}/{data['minor']})"
            else:
                display_name += f"{data.get('id', 'unknown')}"
            
            index = self.device_choice.Append(display_name, key)
            
            if key == selected_key:
                self.device_choice.SetSelection(index)
                self.selected_key = key 