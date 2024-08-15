This is a little hard to use so bear with me

get_token.py:
first make a twitch dev account
make an application with the name of your choice
copy client ID into get_token.py on line 7
generate a secret and copy into get_token.py on line 8
replace the r'your file path\twitch_access_token.txt', make sure the accsess token is a txt

IMPORTANT ABOUT get_token.py:
your authentication code will expire so run this every time you use it
delete the txt file before you run it

TwitchTTS.py:
replace TWITCH_CHANNEL on line 19 with the channel you wish to read out loud, include a # before the username
replace TOKEN_FILE_PATH on line 22 with (twitch_access_token.txt from earlier)'s file path

run.bat:
replace your path here on line 5 with the TwitchTTS.py file path

IMPORTANT INFORMATION IN GENERAL:
Remove extra quote marks, if theres 2 on one side in the things i say to replace, there shouldn't be
Do not share your auth token as this will allow accsess to your twitch, i can not see this as this code is run locally
Do not share your secret, it's in the name

DM me on discord if you have enquiries at britishminute
