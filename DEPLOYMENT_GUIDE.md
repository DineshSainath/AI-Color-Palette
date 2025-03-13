# Deploying Palette AI to Vercel with Supabase

This guide will walk you through deploying your Palette AI application to Vercel with a Supabase PostgreSQL database.

## Prerequisites

- Node.js and npm installed
- Vercel CLI installed (`npm install -g vercel`)
- Supabase account (free tier is sufficient)
- Your Supabase connection string

## Step 1: Set Up Your Local Environment

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your actual values:
   - Your OpenAI API key
   - Your Supabase connection string
   - A secure random string for SECRET_KEY

## Step 2: Initialize Your Supabase Database

1. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the database setup script:

   ```bash
   python setup_db.py
   ```

   This will create all the necessary tables in your Supabase database.

## Step 3: Deploy to Vercel

1. Login to Vercel:

   ```bash
   vercel login
   ```

2. Deploy your application:

   ```bash
   vercel
   ```

   Follow the prompts:

   - Set up and deploy: Yes
   - Link to existing project: No (or Yes if you've deployed before)
   - Project name: palette-ai (or your preferred name)
   - Directory: ./ (current directory)
   - Override settings: No

3. Set environment variables in the Vercel dashboard:

   - Go to your project in the Vercel dashboard
   - Navigate to "Settings" > "Environment Variables"
   - Add the following variables:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `DATABASE_URL`: Your Supabase connection string
     - `SECRET_KEY`: A secure random string
     - `VERCEL_ENV`: Set to "production"

4. Redeploy with environment variables:
   ```bash
   vercel --prod
   ```

## Step 4: Verify Your Deployment

1. Visit your deployed application at the URL provided by Vercel
2. Test user registration and login
3. Test creating and saving color palettes
4. Verify that data is being stored in your Supabase database

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Check your `DATABASE_URL` environment variable in Vercel
2. Ensure your Supabase database is active
3. Verify that your IP is allowed in Supabase network settings

### Application Errors

If your application shows errors:

1. Check the Vercel deployment logs
2. Verify all environment variables are set correctly
3. Try running the application locally with the Supabase connection string

## Maintaining Your Application

### Database Migrations

If you need to make changes to your database schema:

1. Update your models in `models.py`
2. Run the migration script:
   ```bash
   python migrations.py
   ```

### Updating Your Application

1. Make changes to your code
2. Commit to your GitHub repository (if connected)
3. Vercel will automatically deploy the changes
4. Or manually deploy with:
   ```bash
   vercel --prod
   ```

## Monitoring

- Monitor your application performance in the Vercel dashboard
- Check your database usage in the Supabase dashboard
