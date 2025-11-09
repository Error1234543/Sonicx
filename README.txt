TELEGRAM WEBAPP BOT (Koyeb-ready)
--------------------------------
What this package contains:
- bot.py         : Main bot code (uses polling).
- requirements.txt
- Procfile       : For Koyeb run as a worker process.
- runtime.txt    : Python version hint.
- README.txt     : This file.

Quick setup (Koyeb):
1. Create a new Koyeb app (Service). Choose 'Git' or 'Upload ZIP' option.
2. Upload this ZIP or push to a Git repo and connect.
3. In Koyeb service > Settings > Environment Variables, set:
   - BOT_TOKEN : Your Telegram bot token (from @BotFather)
   - CHANNEL_ID: The channel username that users must join (include @), e.g. @neetprepchannel
   - WEB_URL   : Your hosted website URL (https://...), e.g. https://mystudy.vercel.app/index.html
4. Start the service. Koyeb will run 'python bot.py' as long-running worker.
5. Use /start in your bot. Bot will ask users to join the channel; after verification it will show 'OPEN WEBSITE' button.
Notes:
- Telegram WebApp requires an HTTPS URL. Ensure WEB_URL starts with https://
- If your channel is private, the bot must be an admin of that channel to check membership.
- This project uses long polling. Koyeb supports long-running worker processes, so polling works.
- If you prefer webhooks, adjust bot.py to create a small webserver and set webhook URL.
