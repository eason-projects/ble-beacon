#!/usr/bin/env python3
"""
Launcher for BLE Kafka Scanner application.
This script handles permissions and launches the scanner with a GUI.
"""

import os
import sys
import asyncio
import subprocess
import platform
import time
import logging
import threading
import queue
import wx
import wx.lib.scrolledpanel as scrolled
from datetime import datetime

# Set up logging to a file in the user's Documents folder
log_dir = os.path.expanduser("~/Documents/BLE_Kafka_Scanner_Logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"ble_scanner_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# Configure logging
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create a custom logger for the GUI
logger = logging.getLogger('BLEScanner')
logger.setLevel(logging.INFO)

# Add file handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Create a queue for thread-safe logging to the GUI
log_queue = queue.Queue()

print(f"BLE Kafka Scanner started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Log file: {log_file}")

def setup_paths():
    """Set up the Python path to find modules correctly in both bundled and development modes."""
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the parent directory to the path to find the scan module
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # If we're in a bundled app, we need to adjust paths
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        bundle_dir = os.path.dirname(sys.executable)
        if bundle_dir not in sys.path:
            sys.path.insert(0, bundle_dir)
    
    print(f"Python path: {sys.path}")

def check_permissions():
    """Check and request necessary permissions for BLE scanning."""
    if platform.system() == "Darwin":  # macOS
        try:
            # Check if we have Bluetooth permissions
            result = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to get processes whose name is "bluetoothd"'],
                capture_output=True, text=True, check=True
            )
            print("Bluetooth service check result:", result.stdout.strip())
            
            # Request Bluetooth permissions if needed
            subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to keystroke "y" using {command down}'],
                capture_output=True, text=True
            )
            print("Requested Bluetooth permissions")
            
        except subprocess.CalledProcessError as e:
            print(f"Error checking permissions: {e}")
            print(f"Output: {e.output}")

class RedirectText:
    """Redirect stdout to a wx.TextCtrl."""
    def __init__(self, text_ctrl):
        self.text_ctrl = text_ctrl
        
    def write(self, message):
        """Write message to the text control."""
        if message.strip():  # Only process non-empty messages
            log_queue.put(message)
            
    def flush(self):
        """Flush the stream."""
        pass

class RSSIDisplayFrame(wx.Frame):
    """A frame to display RSSI and last seen time in large text."""
    
    def __init__(self, parent, title="RSSI Display"):
        super(RSSIDisplayFrame, self).__init__(parent, title=title, size=(400, 300),
                                              style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Device selection
        device_sizer = wx.BoxSizer(wx.HORIZONTAL)
        device_label = wx.StaticText(self.panel, label="Select Device:")
        self.device_choice = wx.Choice(self.panel, choices=[])
        device_sizer.Add(device_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        device_sizer.Add(self.device_choice, 1, wx.ALL, 5)
        main_sizer.Add(device_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # RSSI display
        rssi_label = wx.StaticText(self.panel, label="RSSI:")
        self.rssi_value = wx.StaticText(self.panel, label="N/A")
        self.rssi_value.SetFont(wx.Font(60, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(rssi_label, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        main_sizer.Add(self.rssi_value, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        # Last seen display
        last_seen_label = wx.StaticText(self.panel, label="Last Seen:")
        self.last_seen_value = wx.StaticText(self.panel, label="N/A")
        self.last_seen_value.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(last_seen_label, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        main_sizer.Add(self.last_seen_value, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        self.panel.SetSizer(main_sizer)
        self.Centre()
        
        # Bind device selection event
        self.device_choice.Bind(wx.EVT_CHOICE, self.on_device_selected)
        
        # Set up a timer to update the display
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_display, self.timer)
        self.timer.Start(500)  # Update every 500ms
        
        # Bind the close event
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        self.selected_key = None
        self.parent = parent
    
    def on_close(self, event):
        """Handle the window closing event."""
        # Stop the timer
        if self.timer.IsRunning():
            self.timer.Stop()
        
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
    
    def update_display(self, event):
        """Update the RSSI and last seen display."""
        if self.selected_key and self.selected_key in self.parent.beacon_data:
            data = self.parent.beacon_data[self.selected_key]
            self.rssi_value.SetLabel(str(data.get('rssi', 'N/A')))
            self.last_seen_value.SetLabel(data.get('last_seen', 'N/A'))
        else:
            self.rssi_value.SetLabel("N/A")
            self.last_seen_value.SetLabel("N/A")

class BLEScannerApp(wx.App):
    """Main GUI application for BLE Scanner."""
    def OnInit(self):
        self.frame = BLEScannerFrame(None, title="BLE Kafka Scanner")
        self.frame.Show()
        return True

class BLEScannerFrame(wx.Frame):
    """Main frame for the BLE Scanner application."""
    def __init__(self, parent, title):
        super(BLEScannerFrame, self).__init__(parent, title=title, size=(800, 600))
        
        self.scanner_thread = None
        self.scanning = False
        self.beacon_data = {}
        self.rssi_display = None
        
        # Create a panel for the main content
        self.panel = wx.Panel(self)
        
        # Create the main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create a control panel
        control_panel = wx.Panel(self.panel)
        control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Add start/stop buttons
        self.start_button = wx.Button(control_panel, label="Start Scanning")
        self.start_button.Bind(wx.EVT_BUTTON, self.on_start_scanning)
        control_sizer.Add(self.start_button, 0, wx.ALL, 5)
        
        self.stop_button = wx.Button(control_panel, label="Stop Scanning")
        self.stop_button.Bind(wx.EVT_BUTTON, self.on_stop_scanning)
        self.stop_button.Disable()
        control_sizer.Add(self.stop_button, 0, wx.ALL, 5)
        
        # Add clear log button
        self.clear_button = wx.Button(control_panel, label="Clear Log")
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear_log)
        control_sizer.Add(self.clear_button, 0, wx.ALL, 5)
        
        # Add RSSI display button
        self.rssi_display_button = wx.Button(control_panel, label="RSSI Display")
        self.rssi_display_button.Bind(wx.EVT_BUTTON, self.on_rssi_display)
        control_sizer.Add(self.rssi_display_button, 0, wx.ALL, 5)
        
        # Add status label
        status_label = wx.StaticText(control_panel, label="Status:")
        control_sizer.Add(status_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.status = wx.StaticText(control_panel, label="Ready")
        self.status.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        control_sizer.Add(self.status, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        control_panel.SetSizer(control_sizer)
        main_sizer.Add(control_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        # Create a notebook for logs and beacons
        self.notebook = wx.Notebook(self.panel)
        
        # Create log panel
        self.log_panel = wx.Panel(self.notebook)
        log_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add text control for logs
        self.log_text = wx.TextCtrl(self.log_panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        log_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)
        self.log_panel.SetSizer(log_sizer)
        
        # Create beacon panel
        self.beacon_panel = wx.Panel(self.notebook)
        beacon_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add list control for beacons
        self.beacon_list = wx.ListCtrl(self.beacon_panel, style=wx.LC_REPORT)
        self.beacon_list.InsertColumn(0, "Type", width=100)
        self.beacon_list.InsertColumn(1, "UUID", width=300)
        self.beacon_list.InsertColumn(2, "Major", width=80)
        self.beacon_list.InsertColumn(3, "Minor", width=80)
        self.beacon_list.InsertColumn(4, "RSSI", width=80)
        self.beacon_list.InsertColumn(5, "Last Seen", width=150)
        beacon_sizer.Add(self.beacon_list, 1, wx.EXPAND | wx.ALL, 5)
        self.beacon_panel.SetSizer(beacon_sizer)
        
        # Add panels to notebook
        self.notebook.AddPage(self.log_panel, "Scanner Log")
        self.notebook.AddPage(self.beacon_panel, "Detected Beacons")
        
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        
        self.panel.SetSizer(main_sizer)
        
        # Redirect stdout to the text control
        sys.stdout = RedirectText(self.log_text)
        
        # Set up a timer for processing log queue
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.process_log_queue, self.timer)
        self.timer.Start(100)  # Check queue every 100ms
        
        # Bind the close event
        self.Bind(wx.EVT_CLOSE, self.on_closing)
        
        # Center the window
        self.Centre()
    
    def process_log_queue(self, event):
        """Process messages in the log queue."""
        while not log_queue.empty():
            message = log_queue.get()
            wx.CallAfter(self.update_log, message)
    
    def update_log(self, message):
        """Update the log text control."""
        # Ensure the message ends with a newline character
        if message is not None:
            self.log_text.AppendText(message + "\n")
    
    def on_start_scanning(self, event):
        """Start BLE scanning."""
        if not self.scanning:
            self.scanning = True
            self.start_button.Disable()
            self.stop_button.Enable()
            self.status.SetLabel("Scanning...")
            
            # Start the scanner in a separate thread
            self.scanner_thread = threading.Thread(target=self.run_scanner)
            self.scanner_thread.daemon = True
            self.scanner_thread.start()
    
    def on_stop_scanning(self, event):
        """Stop BLE scanning."""
        if self.scanning:
            self.scanning = False
            print("Stopping scanner...")
            self.status.SetLabel("Stopping...")
            # The scanner thread will detect self.scanning is False and exit
    
    def run_scanner(self):
        """Run the BLE scanner in a separate thread."""
        try:
            # Import the scan module
            import scan
            
            # Define the beacon callback function
            def beacon_callback(beacon_type, beacon_data):
                """Callback function for beacon updates."""
                wx.CallAfter(self.update_beacon, beacon_type, beacon_data)
            
            # Set the callback in the scan module
            scan.set_gui_callback(beacon_callback)
            
            # Create an event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the scanner
            loop.run_until_complete(self.run_scanner_async(scan))
            
        except Exception as e:
            print(f"Error in scanner thread: {e}")
            import traceback
            traceback.print_exc()
        finally:
            wx.CallAfter(self.scanner_stopped)
    
    async def run_scanner_async(self, scan_module):
        """Run the scanner asynchronously."""
        try:
            # Start scanning
            await scan_module.scan_ble_devices()
            
            # Keep running until scanning is stopped
            while self.scanning:
                await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"Error in async scanner: {e}")
            import traceback
            traceback.print_exc()
    
    def scanner_stopped(self):
        """Called when the scanner has stopped."""
        self.scanning = False
        self.start_button.Enable()
        self.stop_button.Disable()
        self.status.SetLabel("Ready")
        print("Scanner stopped")
    
    def update_beacon(self, beacon_type, beacon_data):
        """Update the beacon list with new data."""
        # Create a unique key for this beacon
        if beacon_type == "iBeacon":
            key = f"{beacon_type}_{beacon_data['uuid']}_{beacon_data['major']}_{beacon_data['minor']}"
        else:
            key = f"{beacon_type}_{beacon_data.get('id', 'unknown')}"
        
        # Store the beacon data for the RSSI display
        current_time = datetime.now().strftime("%H:%M:%S")
        if key not in self.beacon_data:
            self.beacon_data[key] = {
                'type': beacon_type,
                'last_seen': current_time,
                'rssi': beacon_data.get('rssi', 'N/A')
            }
            if beacon_type == "iBeacon":
                self.beacon_data[key].update({
                    'uuid': beacon_data['uuid'],
                    'major': beacon_data['major'],
                    'minor': beacon_data['minor']
                })
            else:
                self.beacon_data[key]['id'] = beacon_data.get('id', 'unknown')
        else:
            self.beacon_data[key]['last_seen'] = current_time
            self.beacon_data[key]['rssi'] = beacon_data.get('rssi', 'N/A')
        
        # Update the RSSI display if it's open
        if self.rssi_display and self.rssi_display.IsShown():
            wx.CallAfter(self.rssi_display.update_device_list, self.beacon_data)
        
        # Check if this beacon is already in our list
        found = False
        for i in range(self.beacon_list.GetItemCount()):
            if self.beacon_list.GetItemData(i) == hash(key):
                found = True
                # Update the existing item
                if beacon_type == "iBeacon":
                    self.beacon_list.SetItem(i, 3, str(beacon_data['minor']))
                    self.beacon_list.SetItem(i, 4, str(beacon_data['rssi']))
                    self.beacon_list.SetItem(i, 5, current_time)
                else:
                    self.beacon_list.SetItem(i, 4, str(beacon_data.get('rssi', 'N/A')))
                    self.beacon_list.SetItem(i, 5, current_time)
                break
        
        # If not found, add a new item
        if not found:
            index = self.beacon_list.InsertItem(self.beacon_list.GetItemCount(), beacon_type)
            
            if beacon_type == "iBeacon":
                self.beacon_list.SetItem(index, 1, str(beacon_data['uuid']))
                self.beacon_list.SetItem(index, 2, str(beacon_data['major']))
                self.beacon_list.SetItem(index, 3, str(beacon_data['minor']))
                self.beacon_list.SetItem(index, 4, str(beacon_data['rssi']))
            else:
                self.beacon_list.SetItem(index, 1, str(beacon_data.get('id', 'unknown')))
                self.beacon_list.SetItem(index, 2, "N/A")
                self.beacon_list.SetItem(index, 3, "N/A")
                self.beacon_list.SetItem(index, 4, str(beacon_data.get('rssi', 'N/A')))
            
            self.beacon_list.SetItem(index, 5, current_time)
            self.beacon_list.SetItemData(index, hash(key))
    
    def on_clear_log(self, event):
        """Clear the log text control."""
        self.log_text.Clear()
    
    def on_rssi_display(self, event):
        """Open or bring to front the RSSI display window."""
        if self.rssi_display is None:
            self.rssi_display = RSSIDisplayFrame(self)
            self.rssi_display.Show()
        else:
            # If the window exists but is hidden, show it
            if not self.rssi_display.IsShown():
                self.rssi_display.Show()
            # Bring it to the front
            self.rssi_display.Raise()
            
        # Update the device list
        if self.rssi_display:
            self.rssi_display.update_device_list(self.beacon_data)
    
    def on_closing(self, event):
        """Handle the window closing event."""
        if self.scanning:
            print("Stopping scanner before exit...")
            self.scanning = False
            # Wait a bit for the scanner to stop
            wx.CallLater(500, self.on_closing, event)
            return
        
        # Close the RSSI display if it's open
        if self.rssi_display is not None:
            # Stop the timer in the RSSI display
            if self.rssi_display.timer.IsRunning():
                self.rssi_display.timer.Stop()
            # Destroy the window
            self.rssi_display.Destroy()
            self.rssi_display = None
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        # Destroy the window
        self.Destroy()

def main():
    """Main function to run the BLE scanner GUI."""
    # Set up paths before importing any modules
    setup_paths()
    
    # Create the GUI
    app = BLEScannerApp(False)
    app.MainLoop()

if __name__ == "__main__":
    main() 