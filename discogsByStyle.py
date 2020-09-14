import requests
import sys


class Record:
    def __init__(self,a,t,g,s,y):
        self.artist = a
        self.title = t
        self.genres = g
        self.styles = s
        self.year = y
        self.decade = self.__decade__(y)

    def __decade__(self, year):
        if year == 0:
            return ("n/a")
        else:
            return str(year - (year % 10))


def main():
    genre_list = []
    style_list = []
    decade_list = []
    coll_size = 0

    # Error Check for proper command line inputs
    if len(sys.argv) != 3 or "-h" in sys.argv:
        print("Usage: discogsByStyle.py <username> <token>\nFind a token here: discogs.com/settings/developers")
        sys.exit()

    print('''
            ***********DISCOGS BY STYLE***********
            * This app will sort your discogs    *
            * collection by style or genre.      *
            * Enter '-h' at anytime for help.    *
            **************************************

Loading your Discogs collection now.  This may take a few seconds...''')

    # Obtain collection from Discogs, sort by artist name, then sort genres and styles alphabetically
    collection = get_vinyl(sys.argv)
    f_collection = format_out(collection, genre_list, style_list, decade_list)
    f_collection.sort(key=lambda x: x.artist)
    coll_size = len(f_collection)
    genre_list.sort()
    style_list.sort()
    decade_list.sort()

    #TODO: add feature to calculate percentage of all styles and genres in your collection

    # User Input
    while True:
        cmd = input("Command: ").lower()
        if cmd == 'k':
            display_keys(style_list, genre_list, decade_list)
        elif cmd in ['s', 'g', 'a', 'o', 'd']:
            display(f_collection, style_list, genre_list, decade_list, cmd, coll_size)
        elif cmd == 'q':
            sys.exit()
        elif cmd == '-h':
            print('''Usage:
            k: Print style, genre, and/or decade sort keys
            a: Print all records in your collection, sorted by artist name
            o: Print your whole collection, with number of records per style, genre, and decade, sorted by total records
            s: Return all records in your collection that match a chosen style, sorted by artist name
            g: Return all records in your collection that match a chosen genre, sorted by artist name
            d: Sorts collection by decade, then choose to either to:
                s: Return all records that match the chosen style AND decade
                g: Return all records that match the chose genre AND decade, or
                a: Print all records in your collection from that decade (xxx0 - xxxx9)
                    NOTE:   not all records in Discogs have year information.  For those records that don't
                            have a year, the year will either appear as '0' or 'n/a'
            q: Quit''')
        else:
            print("Invalid command.  Enter -h for help")


def format_out(coll, g_list, s_list, d_list):
    records = []

    # Create a list of Record objects containing relevant data from Discogs API calls
    for i in range(len(coll)):
        for j in range(len(coll[i]['releases'])):
            title = coll[i]['releases'][j]['basic_information']['title']
            artist = coll[i]['releases'][j]['basic_information']['artists'][0]['name']
            genres = coll[i]['releases'][j]['basic_information']['genres']
            styles = coll[i]['releases'][j]['basic_information']['styles']
            year = coll[i]['releases'][j]['basic_information']['year']

            rec = Record(artist, title, genres, styles, year)
            records.append(rec)

            # Initializing key lists
            for s in styles:
                if not(s in s_list):
                    s_list.append(s)
            for g in genres:
                if not(g in g_list):
                    g_list.append(g)
            if not (rec.decade in d_list):
                d_list.append(rec.decade)

    return records


def display_keys(s_list, g_list, d_list):
    if s_list:
        print(f"Style Keys: {' | '.join(s_list)}\n")
    if g_list:
        print(f"Genre Keys: {' | '.join(g_list)}\n")
    if d_list:
        print(f"Decade Keys: {' | '.join(d_list)}\n")


def display(coll, s_list, g_list, d_list, c, size):
    _opt = ""
    d_opt = 0
    count = 0
    style_stats = []
    genre_stats = []
    decade_stats = []
    all_styles = []
    all_genres = []
    all_decades = []

    # Program branches here based on command input -- set sort_type to _opt to bypass Style/Genre/Decade while loop
    if c == 's':
        sort_type = s_list
        sort_str = "Style"
    elif c == 'g':
        sort_type = g_list
        sort_str = "Genre"
    elif c == 'd':
        sort_type = d_list
        sort_str = "Decade"
    else:
        sort_type = _opt

    while not (_opt in sort_type):
        _opt = input(f"Choose {sort_str}: ")

        if _opt.lower() == '-h':
            print("\nUsage: Enter a key. For list of keys, Press k.\nPress q to quit, Press m to return to main menu\n")
            continue
        elif _opt.lower() == 'k':
            if c == 's':
                display_keys(s_list, 0, 0)
            elif c == 'g':
                display_keys(0, g_list, 0)
            else:
                display_keys(0, 0, d_list)
            continue
        elif _opt.lower() == 'q':
            sys.exit()
        elif _opt.lower() == 'm':
            return

        if c == 'd':
            if _opt not in sort_type:
                print("Invalid Decade. ", end="")
                continue

            d_opt = _opt
            while _opt not in ['s', 'g', 'q', 'a']:
                _opt = input("Choose between Style (s), Genre (g), or All (a): ").lower()
                if _opt == 's':
                    c = 's'
                    sort_str = "Style"
                    sort_type = s_list
                elif _opt == 'g':
                    c = 'g'
                    sort_str = "Genre"
                    sort_type = g_list
                elif _opt == 'q':
                    sys.exit()
                elif _opt == 'a':
                    sort_type = _opt
                elif _opt == 'k':
                    print("\tStyle: s\n\tGenre: g\n\tAll:   a")
                else:
                    print("\tInvalid Command.\n\tEnter s, g or a to continue.  Press k to get keys.  Press q to quit.")

    # Print records to screen in easy to read format
    if d_opt:
        print("-" * 26 + d_opt + "-" * 26)
    else:
        print("-" * 56)

    for record in coll:
        if c == 'a' or (c == 'd' and d_opt in record.decade):
            print(f"{count + 1}. {record.artist} - {record.title} ({record.year})\n\t" +
                  f"Styles: {' | '.join(record.styles)}\n\tGenres: {' | '.join(record.genres)}")
        elif c == 'o':
            # Makes a list containing every occurrence of a style and genre in the collection
            for style in record.styles:
                style_stats.append(style)
            for genre in record.genres:
                genre_stats.append(genre)
            decade_stats.append(record.decade)
        elif c in ['s', 'g'] and (_opt in record.styles or _opt in record.genres):
            if d_opt:
                if d_opt == record.decade:
                    print(f"{count + 1}. {record.artist} - {record.title} ({record.year})")
                    print(f"\tStyles: {' | '.join(record.styles)}\n\tGenres: {' | '.join(record.genres)}")
                else:
                    count -= 1
                    pass
            else:
                print(f"{count + 1}. {record.artist} - {record.title} ({record.year})")
                print(f"\tStyles: {' | '.join(record.styles)}\n\tGenres: {' | '.join(record.genres)}")
        else:
            count -= 1
            pass
        count += 1

    if not(c == 'o'):
        print("-" * 56)
        print(f"Total: {count}", end="")
        if d_opt:
            print(f" from the {d_opt}s", end="")
        if not(c == 'a'):
            print(". Percentage of Collection = {0:.2f} %".format(100 * count/size))
        else:
            print("")
    else:
        # Output formatting for 'o' command
        style_stats.sort()
        genre_stats.sort()
        decade_stats.sort()

        # Counts the number of occurrences of a particular style and creates a tuple, which is then appended
        # to a list of styles.  That list of (style, count) tuples is sorted based on the count, and then printed
        print(" " * 19 + "TOTAL STYLES\n" + ("-" * 56))
        for style in s_list:
            num = style_stats.count(style)
            t = (style, num)
            all_styles.append(t)
        all_styles.sort(key=lambda x: x[1])
        for i in range(len(all_styles)):
            print(str(all_styles[i][0]) + "." * (40-len(all_styles[i][0])), end="")
            print("{:>4} --- {:>5.2f} %".format(all_styles[i][1], (100*(all_styles[i][1]/size))))

        # Performs a similar function as above, but with genre instead of style
        print("-" * 56 + "\n" + " " * 19 + "TOTAL GENRES\n" + ("-" * 56))
        for genre in g_list:
            num = genre_stats.count(genre)
            t = (genre, num)
            all_genres.append(t)
        all_genres.sort(key=lambda x: x[1])
        for i in range(len(all_genres)):
            print(str(all_genres[i][0]) + "." * (40-len(all_genres[i][0])), end="")
            print("{:>4} --- {:>5.2f} %".format(all_genres[i][1], (100*(all_genres[i][1]/size))))

        # Same as above, but with decades
        print("-" * 56 + "\n" + " " * 18 + "TOTAL DECADES\n" + ("-" * 56))
        for decade in d_list:
            num = decade_stats.count(decade)
            t = (decade, num)
            all_decades.append(t)
        all_decades.sort(key=lambda x: x[1])
        for i in range(len(all_decades)):
            if all_decades[i][0] == "0":
                print("n/a" + "." * 37, end="")
            else:
                print(str(all_decades[i][0]) + "." * (40-len(all_decades[i][0])), end="")
            print("{:>4} --- {:5.2f} %".format(all_decades[i][1], (100*(all_decades[i][1]/size))))


def error_check(res):
    # Handling responses other than OK
    if not(res.status_code == 200):
        print("An Error Occurred.  Please Try Again.")
        print(f"Code {res.status_code}: {res.reason}.")
        sys.exit()


def get_vinyl(arg_list):

    # TODO: allow for selection of private folders - current implementation only selects Uncategorized folder
    col_list = []
    url = ("https://api.discogs.com/users/" + arg_list[1] + "/collection/folders/1/releases?token=" + arg_list[2] +
           "&per_page=100")

    response = requests.get(url)
    error_check(response)

    col_dict = response.json()
    col_list.append(col_dict)
    page_num = col_dict['pagination']['pages']

    # Discogs only returns max 100 entries per call - make multiple calls based on number of pages
    for i in range(page_num-1):
        try:
            # Discogs API provides direct link to next page
            col_next = col_dict['pagination']['urls']['next']
        except KeyError:
            print("last page")
            break
        response = requests.get(col_next)
        error_check(response)
        col_dict = response.json()
        col_list.append(col_dict)

    return col_list


if __name__ == "__main__":
    main()