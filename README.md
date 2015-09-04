# LoLAlerter
An open-source version of the LoLAlerter client - http://lolalerter.com/

## Requirements
- Python >= 3.4
- MySQL >= 5

## Development Instructions
1. ```$ pip install```
2. Run db_create.sql
3. Edit ```lolalerter.conf```
4. Edit logging path (Line 29) in ```logging.conf```

**To run**

```python lolalerter/lolalerter.py```

## Administrator Commands
Edit the ```AdminSummoner``` setting in the database to your summoner ID.

The AdminSummoner sending these messages to any bot on your region will produce a result:
- ```!online```: A list of online users
- ```!message {twitch_username} {message}```: Sends an in-game message to a summoner for the given twitch user

## User Commands
Any user sending these messages to their bot will produce a result:
- ```!hi```: Bot will respond with ```Hi``` (easy to test if the bot is active)
- ```!restart```: Bot will restart tracking for the user
