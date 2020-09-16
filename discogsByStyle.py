import requests
import sys
import getopt
import time
import json


class Record:
    def __init__(self, a, t, g, s, y, murl):
        self.artist = a
        self.title = t
        self.genres = g
        self.styles = s
        self.year = y
        self.master_url = murl
        self.reissue_year = 0
        self.reissue = False
        self.decade = self.__decade__(y)

    def __decade__(self, year):
        if year == 0:
            return "n/a"
        else:
            return str(year - (year % 10))


def main(argv):

    genre_list = []
    style_list = []
    decade_list = []
    reissue_num = [0]
    coll_size = 0
    master = False
    reissues = False
    from_file = False
    arg_dict = {}

    # Error check for proper command line inputs
    if not argv:
        print('''Usage: 
                discogsByStyle.py -u <username> [-t <token>] [-i <filepath>] [-r] [-m]
                Find a token here: discogs.com/settings/developers''')
        sys.exit(3)
    try:
        opts, args = getopt.getopt(argv, 'hu:i:t:rm', ['username=', 'token=', 'ifile=', 'reissue', 'master'])
    except getopt.GetoptError:
        print('Invalid input.  Enter -h for usage.')
        sys.exit(2)

    if not opts:
        print("Invalid input.  Enter -h for usage.")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h' or len(argv) == 1:
            print('''           Usage: 
                discogsByStyle.py -u <username> [<-t token>] [-i --ifile filepath] [-m --master]
                    
                An authentication token is needed to use this program
                Find a token here: https://www.discogs.com/settings/developers
                You may need to sign in to your Discogs account first
                
                Quickstart: discogsByStyle -u <your username here> -t <your token here>
                    
            Flags and Options:
                -u or --username : your Discogs username should be entered here
                -t or --token    : load collection from Discogs using your authentication token
                -i or --ifile    : load collection from a saved file
                -r or --reissue  : load data from your reissues' masters on Discogs
                -m or --master   : load data from all your albums' masters on Discogs
                    !!! Masters can only be retrieved at a rate of 1 per second.!!!
                    !!! For larger collections with lots of reissues, loading   !!!
                    !!! from masters may take several minutes.  Loading from    !!!
                    !!! masters is only needed if you want to retrieve original !!! 
                    !!! release dates for your reissues. Otherwise, the year    !!!
                    !!! information for your albums will be the year your       !!!
                    !!! particular pressing was released.                       !!!''')
            sys.exit()
        elif opt in ['-t', '--token']:
            arg_dict['token'] = arg
        elif opt in ['-u', '--username']:
            arg_dict['username'] = arg
        elif opt in ['-i', '--ifile']:
            arg_dict['inputfile'] = arg
            from_file = True
        elif opt in ['-r', '--reissue']:
            reissues = True
        elif opt in ['-m', '--master']:
            master = True

    print('''
            ********************DISCOGS SORTER**********************
            * This app will sort your Discogs collection by style, *
            * by style, genre and/or decade.  View the records in  *
            * your collection that match the selected style or     *
            * genre, with options to further sort by decade, or    *
            * output an overview of your entire collection with    *
            * statistical data. Run with -r or -m flags for more   *
            * accurate and most accurate release date information, *
            * respectively (runtime greatly increases with -m flag)*
            * Enter '-h' at anytime for help.                      *
            ********************************************************

Loading your Discogs collection...''')

    # Obtain collection from Discogs, sort by artist name, then sort genres and styles alphabetically, decades by year
    collection = get_discogs(arg_dict)
    f_collection = format_discogs(collection, genre_list, style_list, decade_list, reissue_num, from_file)
    f_collection.sort(key=lambda x: x.artist)
    if master or reissues:
        get_masters(f_collection, arg_dict['token'], reissue_num, reissues, master)
    coll_size = len(f_collection)

    genre_list.sort()
    style_list.sort()
    decade_list.sort()

    # User Input
    while True:
        cmd = input("Command: ").lower()
        if cmd == 'k':
            display_keys(style_list, genre_list, decade_list)
        elif cmd in ['s', 'g', 'a', 'o', 'd']:
            display(f_collection, style_list, genre_list, decade_list, cmd, coll_size, reissues, master, from_file)
        elif cmd == 'q':
            sys.exit()
        elif cmd == '-h':
            print('''Usage:
            k: Print style, genre, and/or decade sort keys
            a: Print all records in your collection, sorted by artist name
            o: Print a collection overview, with number of records per style, genre, and decade, sorted by total records
            s: Return all records in your collection that match a chosen style, sorted by artist name
            g: Return all records in your collection that match a chosen genre, sorted by artist name
            d: Sorts collection by decade, then choose to either to:
                s: Return all records that match the chosen style AND decade
                g: Return all records that match the chose genre AND decade, or
                a: Print all records in your collection from that decade (xxx0 - xxxx9)
                    NOTE:   not all records in Discogss have year information.  For those records that don't
                            have a year, the year may appear as '0' or 'n/a' 
            e: Export/Save your collection to a file
            q: Quit''')
        elif cmd == 'e':
            json_file(f_collection)
            print(f"Saved {len(f_collection)} records to my_discogs_col.json")
        else:
            print("Invalid command.  Enter -h for help")


def format_discogs(coll, g_list, s_list, d_list, re_s, f_file):

    records = []

    # Create a list of Record objects containing relevant data from Discogs API calls
    if not f_file:
        for i in range(len(coll)):
            for j in range(len(coll[i]['releases'])):
                title = coll[i]['releases'][j]['basic_information']['title']
                artist = coll[i]['releases'][j]['basic_information']['artists'][0]['name']
                genres = coll[i]['releases'][j]['basic_information']['genres']
                styles = coll[i]['releases'][j]['basic_information']['styles']
                year = coll[i]['releases'][j]['basic_information']['year']
                try:
                    master_url = coll[i]['releases'][j]['basic_information']['master_url']
                except KeyError:
                    master_url = None
                format_list = coll[i]['releases'][j]['basic_information']['formats']

                rec = Record(artist, title, genres, styles, year, master_url)

                for f in range(len(format_list)):
                    try:
                        if 'Reissue' in format_list[f]['descriptions']:
                            rec.reissue = True
                            re_s[0] += 1
                    except KeyError:
                        # box sets include a format which does not contain a 'descriptions' tag
                        pass

                records.append(rec)
                initialize_lists(s_list, g_list, d_list, rec)
    else:
        for i in range(len(coll)):
            title = coll[i]['title']
            artist = coll[i]['artist']
            genres = coll[i]['genres']
            styles = coll[i]['styles']
            year = coll[i]['year']
            master_url = coll[i]['master_url']

            rec = Record(artist, title, genres, styles, year, master_url)
            rec.reissue_year = coll[i]['reissue_year']
            rec.reissue = coll[i]['reissue']
            records.append(rec)
            initialize_lists(s_list, g_list, d_list, rec)

    return records


def initialize_lists(sl, gl, dl, rcd):
    # Initializing key lists
    for s in rcd.styles:
        if not(s in sl):
            sl.append(s)
    for g in rcd.genres:
        if not(g in gl):
            gl.append(g)
    if not (rcd.decade in dl):
        dl.append(rcd.decade)


def display_keys(s_list, g_list, d_list):

    if s_list:
        print(f"Style Keys: {' | '.join(s_list)}\n")
    if g_list:
        print(f"Genre Keys: {' | '.join(g_list)}\n")
    if d_list:
        print(f"Decade Keys: {' | '.join(d_list)}\n")


def display(coll, s_list, g_list, d_list, c, size, r, m, ff):

    _opt = ""
    sort_str = ""
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
        elif _opt.lower() == 'e':
            json_file(coll)
            print(f"Save {size} records to my_discogs_col.json")
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
                elif _opt == 'm':
                    return
                elif _opt == 'a':
                    sort_type = _opt
                elif _opt == 'k':
                    print("\ts: Sort by style\n\tg: Sort by genre\n\ta: Print all from this decade")
                elif _opt == 'e':
                    json_file(coll)
                    print(f"Saved {size} records to my_discogs_col.json.")
                else:
                    print('''Usage:
            Enter s, g or a to select a sort method
            Press k to get keys
            Press m to return to the main menu
            Press e to save collection to file
            Press q to quit.''')

    # Print records to screen in easy to read format
    if d_opt:
        print("-" * 26 + d_opt + "-" * 26)
    else:
        print("-" * 56)

    for record in coll:
        if record.reissue and (r or m or ff):
            r_str = "\n    (R): " + str(record.reissue_year)
        else:
            r_str = ""

        if c == 'a' or (c == 'd' and d_opt in record.decade):
            print(f"{count + 1}. {record.artist} - {record.title} ({record.year}){r_str}\n\t" +
                  f"Styles: {' | '.join(record.styles)}\n\tGenres: {' | '.join(record.genres)}")
        elif c == 'o':
            # Makes a list containing every occurrence of a style and genre in the collection
            # TODO: move stat collection to separate function?
            for style in record.styles:
                style_stats.append(style)
            for genre in record.genres:
                genre_stats.append(genre)
            decade_stats.append(record.decade)
        elif c in ['s', 'g'] and (_opt in record.styles or _opt in record.genres):
            if d_opt:
                if d_opt == record.decade:
                    print(f"{count + 1}. {record.artist} - {record.title} ({record.year}){r_str}")
                    print(f"\tStyles: {' | '.join(record.styles)}\n\tGenres: {' | '.join(record.genres)}")
                else:
                    count -= 1
                    pass
            else:
                print(f"{count + 1}. {record.artist} - {record.title} ({record.year}){r_str}")
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
        print("-" * 56 + "\nFor most accurate Total Decade data, run program with -m")


def error_check(res):
    # Handling responses other than OK
    if not(res.status_code == 200):
        print("An Error Occurred.  Please Try Again.")
        print(f"Code {res.status_code}: {res.reason}.")
        if res.status_code == 429:
            print("Please wait one minute before retrying")
        elif res.status_code == 401:
            print("Please enter a valid token")
        sys.exit(4)


def get_discogs(arg_d):

    # TODO: allow for selection of private folders - current implementation only selects Uncategorized folder
    col_list = []
    try:
        url = ("https://api.discogs.com/users/" + arg_d['username'] + "/collection/folders/1/releases?token=" +
               arg_d['token'] + "&per_page=100")

        response = requests.get(url)
        error_check(response)

        col_dict = response.json()
        col_list.append(col_dict)
        page_num = col_dict['pagination']['pages']

        # Discogs only returns max 100 entries per call - make multiple calls based on number of pages
        for i in range(page_num - 1):
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

    except KeyError:
        try:
            col_list = json_file(0, arg_d['inputfile'])
            return col_list
        except KeyError:
            print("Something went wrong.  Exiting")
            sys.exit(1)


def get_masters(coll, token, num_r, r, m):

    wait_str = ""
    time_tup = ()

    # Estimated wait time based on number of reissues
    if __name__ == "__main__":
        if r:
            time_tup = divmod(num_r[0], 60)
            wait_str = "reissues'"
        elif m:
            time_tup = divmod(len(coll), 60)
            wait_str = "all"

        print(f"Loading {wait_str} master release dates..." +
              "\nEstimated wait time: {0} minutes and {1} seconds".format(time_tup[0], time_tup[1]))

    # Sleep for a few seconds based on the number of previously made API calls to avoid 429 Response
    start_sleep = int(len(coll)/100 + 1)
    time.sleep(start_sleep)
    sleep_time = 1

    for record in coll:
        if not record.reissue:
            if r:
                continue
            elif m:
                pass

        if record.master_url is None:
            continue

        url = record.master_url + "?token=" + token
        response = requests.get(url)
        error_check(response)

        # Optimization for smaller reissue collections
        if num_r[0] + start_sleep < int(response.headers['X-Discogs-Ratelimit-Remaining']) and r:
            sleep_time = 0

        rec_dict = response.json()

        if not record.reissue:
            record.year = rec_dict['year']
        else:
            record.reissue_year = record.year
            record.year = rec_dict['year']

        record.decade = record.__decade__(record.year)
        time.sleep(sleep_time)


def json_file(coll, f_in=0):
    j_list = []

    if not f_in:
        for r in coll:
            j_list.append(vars(r))
        with open('my_discogs_col.json', 'w') as fout:
            json.dump(j_list, fout)
    else:
        with open(f_in, 'r') as read_file:
            coll_data = json.load(read_file)
        return coll_data

    # TODO: re_load function to update file without full call to get_master? Make normal api call,
    #  compare names, make calls if needed or delete if not present


if __name__ == "__main__":
    main(sys.argv[1:])
