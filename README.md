# Discogs Sorting Program
Retrieves and sorts your Discogs collection so you can view albums by style, genre and decade of release
# Description
Discogs.com is an online database where users can keep track of their record collection.
As of 9/1/2020, Discogs's website and its API do not allow for users to sort their collections by style.
This program will retrieve your collection from your "Uncategorized" folder and allow you to sort your collection
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
<pre>python discogsByStyle.py [user name] [token]</pre>
### Command Line Flags
-h: Help.  Prints usage
### Program Commands
<ul>Main Menu
<ul><li>&nbsp;k: Prints style, genre and/or decade keys<br>
<li>&nbsp;a: Will print all records in your collection, sorted by artist name<br>
<li>&nbsp;o: Prints your whole collection, including the number of records per style, per genre, and per decade<br>
<li>&nbsp;s: Returns all records in your collection that match the selected style, sorted by artist name<br>
<li>&nbsp;g: Returns all records in your collection that match the selected genre, sorted by artist name<br>
<li>&nbsp;d: Sorts collection by decade, then choose either to:<br>
<ul><li>s: Return all records that match the chosen style AND decade<br>
<li>g: Return all records that match the chosen genre AND decade<br>
<li>a: Return all records that match teh chosen decade</li></ul>
<li>-h: Help - displays usage<br>
<li>&nbsp;q: Quit</li></ul></ul>
<ul>Choose Style/Genre/Decade Menu
<ul><li>&nbsp;k: Prints style, genre, or decade keys</li>
<li>&nbsp;-h: Help - displays usage</li>
<li>&nbsp;m: Return to main menu</li>
<li>&nbsp;q: Quit</li></ul></ul>

# Print Format
### Printing by Style or Genre
<pre>[#]. [Artist Name] - [Record Title] ([Year])
    Styles: [Styles]
    Genres: [Genres]
.
.
-------------------------------------------------------
Total: [Total Records Returned]. Percentage of Collection = [Percentage of Total Collection] %
</pre>
### Printing All
<pre>[#]. [Artist Name] - [Record Title] ([Year])
    Styles: [Styles]
    Genres: [Genres]
.
.
-------------------------------------------------------
Total: [Total Records Returned]</pre>
### Printing with Decade
<pre>
------------------------------[Decade]------------------------------
[#]. [Artist Name] - [Record Title] ([Year])
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
                      
</pre>
# Limitations
<ul><li>Printing all records while sorting by style and genre is currently not supported, although I'm not sure that would be a 
useful feature.<br><br>

<li>Sorting categorized folders is also currently not supported, but may be implemented in the future.<br><br>

<li>Discogs dates the records in your collection based on the year the particular version of the album was released.
 Thus, the "year" field does not reliably return accurate information about the year the album was originally released 
 (if the record in your collection is a reissue, Discogs will store the year that the reissue came out as the album's
    release year).  This makes this program an unreliable method for sorting records by decade.  
    <ul>This could be corrected by obtaining the master_id (if available) and making a separate call to the API, but
    Discogs throttles calls to 60 per minute at the most.  This would greatly increase the program's runtime and make it
    nearly unusable in its current implementation.
    </ul><br>

<li>Not all records on Discogs have 'year' data, making records of certain eras unsortable by decade.  This is more of a
problem with the data set than with the program.<br><br>

<li>Styles and genres must be typed exactly as they appear (including punctuation) or else no results will be returned.  
This makes searching for longer styles and genres (.e.g "Folk, World, & Country") a little tedious.<br><br>

<li>A token must be obtained before using this program, and only your personal collection can be viewed. Discogs supports
OAuth, but requires additional steps to register and use the service.  Since the purpose of this app is to sort and view
your own collection and not the collection of others, it was easier to implement with a token for personal use than to
go through the trouble of registering and rewriting the program.  Nothing is written in stone, however, so this may 
change in a future version.</li></ul>
