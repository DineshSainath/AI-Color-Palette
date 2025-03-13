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

## Local Development

1. Establish virtual python environment

   - `source env/Scripts/activate` (Windows)
   - `source env/bin/activate` (Mac/Linux)

2. To run with flask use: `flask run`

3. To run the server with live changes:
   - `python app.py`

## Deployment on Vercel

This application is configured for deployment on Vercel. To deploy:

1. Install Vercel CLI:

   ```
   npm install -g vercel
   ```

2. Login to Vercel:

   ```
   vercel login
   ```

3. Deploy the application:

   ```
   vercel
   ```

4. Set up environment variables in the Vercel dashboard:

   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SECRET_KEY`: A secure random string for Flask sessions
   - `DATABASE_URL`: URL for your database (if using a cloud database)

5. For production deployment:
   ```
   vercel --prod
   ```

## Database Configuration

For local development, the application uses SQLite. For production on Vercel, you should use a cloud database like PostgreSQL.
