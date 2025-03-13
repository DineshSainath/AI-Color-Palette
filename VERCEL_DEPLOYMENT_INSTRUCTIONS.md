# Vercel Deployment Instructions for Palette AI

## Prerequisites

1. Node.js and npm installed on your computer
2. A Vercel account (sign up at vercel.com)
3. A cloud database (recommended: PostgreSQL on Railway, Supabase, or Neon)

## Step 1: Set Up Your Database

Since Vercel's serverless environment doesn't support SQLite, you need a cloud database:

1. Sign up for a free PostgreSQL database:

   - [Railway](https://railway.app/)
   - [Supabase](https://supabase.com/)
   - [Neon](https://neon.tech/)

2. Create a new PostgreSQL database

3. Get your database connection string, which will look something like:
   ```
   postgresql://username:password@hostname:port/database
   ```

## Step 2: Install Vercel CLI

```bash
npm install -g vercel
```

## Step 3: Login to Vercel

```bash
vercel login
```

## Step 4: Deploy Your Application

From your project directory, run:

```bash
vercel
```

Follow the prompts:

- Set up and deploy: Yes
- Link to existing project: No
- Project name: palette-ai (or your preferred name)
- Directory: ./ (current directory)
- Override settings: No

## Step 5: Set Environment Variables

After the initial deployment, go to the Vercel dashboard:

1. Select your project
2. Go to "Settings" > "Environment Variables"
3. Add the following variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SECRET_KEY`: A secure random string (run `python -c "import secrets; print(secrets.token_hex(16))"` to generate one)
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `VERCEL_ENV`: Set to "production"

## Step 6: Redeploy with Environment Variables

```bash
vercel --prod
```

## Step 7: Verify Deployment

1. Visit your deployed application at the URL provided by Vercel
2. Test all functionality to ensure it works correctly

## Troubleshooting

If you encounter issues:

1. Check the Vercel deployment logs in the dashboard
2. Ensure all environment variables are set correctly
3. Verify your database connection string is correct
4. Check that your database tables are created properly

## Maintaining Your Deployment

- Each time you push to your connected GitHub repository, Vercel will automatically redeploy
- You can manually trigger deployments with `vercel --prod`
- Monitor your application's performance in the Vercel dashboard
