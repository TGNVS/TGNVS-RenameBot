if [ -z https://gitlab.com/nvsdrive19/TGNVS-RENAME_BOT ]
then
  echo "Cloning main Repository"
  git clone https://gitlab.com/nvsdrive19/TGNVS-RENAME_BOT.git /TGNVS-RENAME_BOT
else
  echo "Cloning Custom Repo from https://github.com/gitdrive5/DTG-linkszad-bot "
  git clone https://gitlab.com/nvsdrive19/TGNVS-RENAME_BOT /TGNVS-RENAME_BOT
fi
cd /TGNVS-RENAME_BOT
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 app.py & python3 bot.py
