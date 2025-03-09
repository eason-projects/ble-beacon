import wx

# 1. Create a basic application object
app = wx.App()

# 2. Create the main window (Frame)
frame = wx.Frame(None, title="wxPython Hello World Demo", size=(300, 200))

# 3. Create a static text control to display "Hello, World!"
panel = wx.Panel(frame) # Panels are often used to group controls
hello_text = wx.StaticText(panel, label="Hello, World!", pos=(100, 50)) # position is relative to the panel

# 4. Show the Frame (window)
frame.Show(True)

# 5. Start the event loop
app.MainLoop()