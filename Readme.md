# ColorPalette

## Description

ColorPalette is a simple and intuitive application designed to help users create, manage, and share color palettes. Whether you are a designer, artist, or developer, this tool will assist you in finding the perfect color combinations for your projects.

## Features

- Create custom color palettes
- Save and manage multiple palettes
- Copy hex codes with just a click

## Usage

1. Open the application in your browser.
2. Use the color picker to select colors and add them to your palette.

## Notes

1. Establish virtual python environment

- source env/Scripts/activate

2. To run with flask use: flask run

3. To run the server with live changes:

- pip install livereload
- from livereload import Server
- if **name** == "**main**":
  server = Server(app.wsgi*app) # Create a livereload server
  server.watch('templates/*.html') # Watch HTML changes
  server.watch('static/\*.css') # Watch CSS changes
  server.serve(port=5000, debug=True)
