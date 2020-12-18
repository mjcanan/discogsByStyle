# Discogs Sorting Program
Retrieves and sorts your Discogs collection so you can view albums by style, genre and decade of release
# Description
Discogs.com is an online database where users can keep track of their record collection.
As of 9/1/2020, Discogs's website and its API do not allow for users to sort their collections by style.
This program will retrieve your collection from your "All" folder and allow you to sort your collection
by style, genre and/or decade.<br><br>Once a sort method is chosen, the program will return a numbered list of all the records 
in your collection which belong to that style, genre, and/or decade.  Included is an option to print all of your records, 
with information about style and genre included.  The decade option can be selected in conjunction with style or genre
to further refine your return results.<br><br>Lastly, you can print an overview of your collection, which returns
statistical information about your collection, broken down by style, genre and decade.
  
# Usage
To use this program, you will need your Discogs username and an authorization token.
An authorization token can be found <a href="https://www.discogs.com/settings/developers">here</a>.
You may need to sign in first.
<br>
<br>
Once you have your token, enter the following on the command line:
<br>
<pre>python discogsByStyle.py [-u, --username] username [-t, --token] token</pre>
You can save your collection to a file and load from that in future (which is significantly faster), with the following
command:
<pre>python discogsByStyle.py [-i, --ifile] my_discogs_col.json </pre>
The program will save your collection in your pwd as a JSON file.
### Command Line Arguments
#### Flags
-h: Help.  Prints usage<br>
-r: Loads the original release dates for all of your reissues<br>
-m: Pulls data from the master releases (very time intensive due to rate limiting, but will provide most accurate
release date information)<br>
#### Options
-u [--username] <user_name>: Discog's username - needed if pulling data from Discogs
-t [--token] <token>: Token for accessing Discogs - needed if pulling data from Discogs
-i [--ifile] <filepath>: Input file - needed if you are loading from a saved file and not Discogs API [NOT CURRENTLY IMPLEMENTED]<br>
### Program Commands
<ul>Main Menu
<ul><li>&nbsp;k: Prints style, genre and/or decade keys<br>
<li>&nbsp;a: Will print all records in your collection, sorted by artist name<br>
<li>&nbsp;o: Prints a collection overview, including the number of records per style, per genre, and per decade<br>
<li>&nbsp;s: Returns all records in your collection that match the selected style, sorted by artist name<br>
<li>&nbsp;g: Returns all records in your collection that match the selected genre, sorted by artist name<br>
<li>&nbsp;d: Sorts collection by decade, then choose either to:<br>
<ul><li>s: Return all records that match the chosen style AND decade<br>
<li> g: Return all records that match the chosen genre AND decade<br>
<li> a: Return all records that match the chosen decade</li></ul>
<li> r: Returns a random record from your collection - allows for filtering<br>
<li>-h: Help - displays usage<br>
<li> e: Export/Save your loaded Discog's collection to a file for easier loading in the future<br>
<li>&nbsp;q: Quit</li></ul></ul>
<ul>Choose Style/Genre/Decade Menu
<ul><li>&nbsp;k: Prints style, genre, or decade keys</li>
<li>&nbsp;-h: Help - displays usage</li>
<li>&nbsp;m: Return to main menu</li>
<li> e: Export/Save file</li>
<li> u: Update a collection loaded from a file with latest data from Discogs</li>
<li>&nbsp;q: Quit</li></ul></ul>

# Print Format
### Printing by Style or Genre
<pre>[#]. [Artist Name] - [Record Title] ([Year of Your Pressing (or Master if -r/-m)])
    [(R): [Year Your Pressing Was Issued] -- only if -r or -m flag used]
    Styles: [Styles]
    Genres: [Genres]
.
.
-------------------------------------------------------
Total: [Total Records Returned]. Percentage of Collection = [Percentage of Total Collection] %
</pre>
### Printing All
<pre>[#]. [Artist Name] - [Record Title] ([Year of Your Pressing (or Master if -r/-m)])
    [(R): [Year Your Pressing Was Issued] -- only if -r or -m flag was used]
    Styles: [Styles]
    Genres: [Genres]
.
.
-------------------------------------------------------
Total: [Total Records Returned]</pre>
### Printing with Decade
<pre>
------------------------------[Decade]------------------------------
[#]. [Artist Name] - [Record Title] ([Year of Your Pressing (or Master if -r/-m)])
    [(R): [Year Your Pressing Was Issued] -- only if -r or -m flag used]
    Styles: [Styles]
    Genres: [Genres]
.
.
--------------------------------------------------------------------
Total: [Total Records Returned] from [Decade]s.  Percentage of Collection = [Percentage of Total Collection] %
</pre>
### Printing Overview
<pre>
                         TOTAL STYLES
------------------------------------------------------------
[Style]............[Number of Records] --- [% of Collection]
.
.
------------------------------------------------------------
                         TOTAL GENRES
------------------------------------------------------------
[Genre]............[Number of Records] --- [% of Collection]
.
.
------------------------------------------------------------
                         TOTAL DECADES
------------------------------------------------------------
[Decade]...........[Number of Records] --- [% of Collection]
.
.
For most accurate Total Decade data, run program with -m</pre>
# Limitations
<ul><li>Printing all records while sorting by style and genre is currently not supported, although I'm not sure that would be a 
useful feature.</li>
<li>Sorting categorized folders is also currently not supported, but may be implemented in the future.</li>
<li>Single call to API for user's collection doesn't necessarily return accurate dates for album releases.</li>
<li>Some albums have year value of '0', and other albums have reissue release date and not master release dates.  This is 
solved using -r or -m flags, performance suffers if you have a large collection of reissues or use -m due to rate 
limiting (60 calls per minute).</li>
<li>Styles and genres must be typed exactly as they appear (including punctuation) or else no results will be returned.  
This makes searching for longer styles and genres (.e.g "Folk, World, & Country") a little tedious.</li>
<li>A token must be obtained before using this program, and only your personal collection can be viewed. Discogs supports
OAuth, but requires additional steps to register and use the service.  Since the purpose of this app is to sort and view
your own collection and not the collection of others, it was easier to implement with a token for personal use than to
go through the trouble of registering and rewriting the program.  Nothing is written in stone, however, so this may 
change in a future version.</li></ul>

# Dependencies
<li>requests
<li>sys
<li>getopt
<li>time
<li>json
<li>random
</li>

# Features to Add/Revise
[ ] Load from file while running program<br>
[ ] Allow users to choose sort keys<br>
[ ] Filter function to allow sorting by multiple styles/genres/decades<br>
[X] Allow users to choose Discogs folder<br>
[X] User selected file names<br>
[ ] Optimize sorting and searching in update function<br>
[ ] Improve key display<br>
