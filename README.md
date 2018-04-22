# TwitterC2
A Command&amp;Control server using Twitter's API.

# Disclaimer/ Warning
I do not intend for this to be used illegally and do not take any responsibility for whatever happens. This is still a work-in-progress so expect some bugs.

# Setup
For this, you will need preferably two Twitter accounts. One for the server (controller), and one for the agents (infected computers).
On each account, create an app (by going to https://apps.twitter.com/app/create).
Then, change each apps permissions to allow them to access direct messages.
Next, edit the "keys.txt" file in the main folder. Replace as follows:

  consumer_key=XXXX where "XXXX" is the server's Consumer Key
  
  consumer_secret=XXXX where "XXXX" is the serevr's Consumer Secret
  
  access_token=XXXX where "XXXX" is the server's Access Token (you will need to click the "generate access tokens" button for this)
  
  access_secret=XXXX where "XXXX" is the server's Access Secret
  
  username=XXXX where "XXXX" is the server's username
  
  agent_user=XXXX where "XXXX" is the username of the agents account

Now,  for the "keys.txt" file in the "templates" folder, replace each line with their respective values.

And that's it! Just run the "twitterc2.py" file to begin. To generate a payload, use the "genPayload" command.
