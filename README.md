# Discogs Sorting App
Retrieves and sorts your discogs collection so you can view albums by style and genre
# Description
Discogs.com is an online database where users can keep track of their record collection.
As of 9/1/2020, Discogs's website and its API do not allow for users to sort their collections by style.
This program will retrieve your collection from your "Uncategorized" folder and allow you to sort your collection
by style and genre.  Once a sort method is chosen, the program will return a numbered list of all the records in your
collection which belong to that genre.
# Usage
To use this program, you will need a your discog's username and an authorization token.
An authorization token can be found <a href="https://www.discogs.com/settings/developers">here</a>.
You may need to sign in first.
<br>
<br>
Once you have your token, enter the following on the command line:
<br>
discogsByStyle.py [user name] [token]
<br>

<u>Flags</u>:<br>
-h for help

<u>Commands</u>:<br>
k: get sort keys<br>
g: sort by genre<br>
s: sort by style<br>
-h: help<br>
q: quit<br>

# Return Format
[#]. [Artist Name] - [Record Title] --- [List of All Genres or Styles for the Record]<br>.<br>.
<br>-------------------------------------------------------<br>
[Total Records Returned] [Percentage of Total Collection]
