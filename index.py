#!/usr/bin/python3
# -*- coding: utf-8 -*

import cgi 
import os


# init file path
directory = '/home/pi/photobooth_images'
if os.path.exists('/media/pi/F866-6C99/Photos'):
  directory = '/media/pi/F866-6C99/Photos'


form = cgi.FieldStorage()
print("Content-type: text/html; charset=utf-8\n")

html_start = """<!DOCTYPE html>
<head>
    <title>Mon programme</title>
</head>
<body>
"""

html_end = """
</body>
</html>
"""

#insert header
print(html_start)

#insert images
#to be done

# insert footer
print(html_end)