# Discogs Sorting Program
Retrieves and sorts your Discogs collection so you can view albums by style and genre
# Description
Discogs.com is an online database where users can keep track of their record collection.
As of 9/1/2020, Discogs's website and its API do not allow for users to sort their collections by style.
This program will retrieve your collection from your "Uncategorized" folder and allow you to sort your collection
by style and genre.  Once a sort method is chosen, the program will return a numbered list of all the records in your
collection which belong to that style or genre.  Included is an option to print all of your records, with information 
about style and genre included.
# Usage
To use this program, you will need your Discogs username and an authorization token.
An authorization token can be found <a href="https://www.discogs.com/settings/developers">here</a>.
You may need to sign in first.
<br>
<br>
Once you have your token, enter the following on the command line:
<br>
<pre>python discogsByStyle.py [user name] [token]</pre>
### Flags
-h: Help.  Prints usage
### Commands
 k: Prints style and genre keys<br>
 a: Will print all records in your collection, sorted by artist name<br>
 s: Returns all records in your collection that match the selected style, sorted by artist name<br>
 g: Returns all records in your collection that match the selected genre, sorted by artist name<br>
-h: Help<br>
 q: Quit
# Return Format
### Sorting by Style or Genre
<pre>[#]. [Artist Name] - [Record Title] --- [List of All Genres or Styles for the Record]
.
.
-------------------------------------------------------
Total: [Total Records Returned]. Percentage of Collection = [Percentage of Total Collection] %
</pre>
### Printing All
<pre>[#]. [Artist Name] - [Record Title]
    Styles: [Styles]
    Genres: [Genres]
.
.
-------------------------------------------------------
Total: [Total Records Returned]</pre>
# Limitations
Printing all records while sorting by style and genre is currently not supported, although I'm not sure that would be a 
useful feature.  Sorting categorized folders is also currently not supported, but may be implemented in the future, 
along with additional sort criteria, such as a "Sort by Decade" feature.<br><br>
Styles and genres must be typed exactly as they appear (including punctuation) or else no results will be returned.  
This makes searching for longer styles and genres (.e.g "Folk, World, & Country") a little tedious.<br><br>
A token must be obtained before using this program, and only your personal collection can be viewed. Discogs supports
OAuth, but requires additional steps to register and use the service.  Since the purpose of this app is to sort and view
your own collection and not the collection of others, it was easier to implement with a token for personal use than to
go through the trouble of registering and rewriting the program.  Nothing is written in stone, however, so this may 
change in a future version.
