import requests
import sys
import getopt
import time
import json
import random

class Discogs_Collection:
    def __init__(self, user="", token="", inputFile="", fileFolder=0):
        self.collection = []
        self.user = user
        self.token = token
        self.inputFile = inputFile
        self.fileFolder = fileFolder
        self.decade_list = []
        self.genre_list = []
        self.style_list = []
        self.reissue_num = 0

        #if given input file, load from file and get keys, else load from discogs and get keys
        if inputFile:
            self.__load_from_file__()
        else:
            self.__load_from_discogs__()

    def __load_from_file__(self):
        with open(self.inputFile, 'r') as read_file:
            self.collection = json.load(read_file)
        records = []
        for i in range(len(self.collection[1])):
            title = self.collection[1][i]['title']
            artist = self.collection[1][i]['artist']
            genres = self.collection[1][i]['genres']
            styles = self.collection[1][i]['styles']
            year = self.collection[1][i]['year']
            master_url = self.collection[1][i]['master_url']
            instance_id = self.collection[1][i]['instance_id']
            labels = self.collection[1][i]['labels']

            rec = Record(artist, title, genres, styles, year, master_url, instance_id, labels)
            rec.reissue_year = self.collection[1][i]['reissue_year']
            rec.reissue = self.collection[1][i]['reissue']
            records.append(rec)

        collection_info = self.collection[0]
        self._initialize_key_lists(rec)
        self.collection = collection_info
        self.collection.append(records)

    def __load_from_discogs__(self):
        #use self.fileFolder, make request, then format the data
        coll_list = []
        try:
            url = f"https://api.discogs.com/users/{self.user}/collection/folders/{self.fileFolder}" \
                  f"/releases?token={self.token}&per_page=100"
            response = requests.get(url)
            self.__error_check(response)
            coll_dict = response.json()
            coll_list.append(coll_dict)
            page_num = coll_dict['pagination']['pages']

            # Discogs only returns max 100 entries per call - make multiple calls based on number of pages
            for i in range(page_num - 1):
                try:
                    # Discogs API provides direct link to next page
                    coll_next = coll_dict['pagination']['urls']['next']
                except KeyError:
                    # Last page won't have next url
                    break
                response = requests.get(coll_next)
                Discogs_Collection.__error_check(response)
                coll_dict = response.json()
                coll_list.append(coll_dict)
        except KeyError:
            print("Something went wrong.  Exiting")
            sys.exit(1)
        except requests.exceptions.ConnectionError:
            print("ConnectionError: Max retries exceeded.  No connection established.\nExiting...")
            sys.exit(4)
        self.__format_collection(coll_list)

    def __format_collection(self, coll):
        formatted_collection = []
        collection_info = {}
        records = []

        # Create a list of Record objects containing relevant data from Discogs API call
        collection_info['date_created'] = time.localtime()
        collection_info['date_last_save'] = 0
        collection_info['total'] = coll[0]['pagination']['items']
        collection_info['master_data'] = False
        collection_info['reissue_data'] = False
        # Getting record information from coll
        for i in range(len(coll)):
            for j in range(len(coll[i]['releases'])):
                title = coll[i]['releases'][j]['basic_information']['title']
                artist = coll[i]['releases'][j]['basic_information']['artists'][0]['name']
                genres = coll[i]['releases'][j]['basic_information']['genres']
                styles = coll[i]['releases'][j]['basic_information']['styles']
                year = coll[i]['releases'][j]['basic_information']['year']
                instance_id = coll[i]['releases'][j]['instance_id']
                try:
                    master_url = coll[i]['releases'][j]['basic_information']['master_url']
                except KeyError:
                    master_url = None
                format_list = coll[i]['releases'][j]['basic_information']['formats']
                label_list = coll[i]['releases'][j]['basic_information']['labels']

                rec = Record(artist, title, genres, styles, year, master_url, instance_id, label_list)

                for f in range(len(format_list)):
                    try:
                        if 'Reissue' in format_list[f]['descriptions']:
                            rec.reissue = True
                            self.reissue_num += 1
                    except KeyError:
                        # box sets include a format which does not contain a 'descriptions' tag
                        pass
                records.append(rec)
                self._initialize_key_lists(rec)

        collection_info['styles'] = self.style_list
        collection_info['genres'] = self.genre_list
        collection_info['decades'] = self.decade_list
        formatted_collection.append(collection_info)
        formatted_collection.append(records)
        formatted_collection[1].sort(key=lambda x: x.artist)
        self.collection = formatted_collection

    def _get_folders(self): #TODO
        return

    def __error_check(self,res):
        # Handling responses other than OK
        if not res.ok:
            print(f"An Error Occurred --  Code {res.status_code}: {res.reason}.")
            if res.status_code == 429:
                print("Please wait one minute before retrying.")
            elif res.status_code == 401:
                 print("Please check that your token is valid and try again.")
            sys.exit(4)
        return 0

    def _initialize_key_lists(self, record):
        # Initializing key lists
        for s in record.styles:
            if not (s in self.style_list):
                self.style_list.append(s)
        for g in record.genres:
            if not (g in self.genre_list):
                self.genre_list.append(g)
        if not (record.decade in self.decade_list):
            self.decade_list.append(record.decade)

    def save_collection(self, save_as):
        j_list = []
        j_out = []
        #If user chooses save as, or has no inputfile, then prompt for file
        if save_as or not self.inputFile:
            self.collection[0]['inputfile'] = input("Save File As: ") + ".json"
        j_out.append(self.collection[0])
        for record in self.collection[1]:
            j_list.append(vars(record))
            j_out.append(j_list)
        with open(f"{self.collection[0]['inputfile']}", 'w') as fout:
            json.dump(j_out, fout)

    def display_keys(self):
        self.display_genre_keys()
        self.display_style_keys()
        self.display_decade_keys()

    def display_genre_keys(self):
        print(f"\nGenre Keys: {len(self.genre_list)}\n")
        out = self._key_format(self.genre_list)
        print(out)

    def display_decade_keys(self):
        print(f"\nDecade Keys: {len(self.decade_list)}\n")
        out = self._key_format(self.decade_list)
        print(out)

    def display_style_keys(self):
        print(f"\nStyle Keys: {len(self.style_list)}\n")
        out = self._key_format(self.style_list)
        print(out)

    def _key_format(self, x_list):
        x = divmod(len(x_list), 7)
        remainder = x[1]
        breaks = x[0]
        x_index = 0
        str = ''

        while breaks:
            str += " | ".join(x_list[x_index:x_index + 7]) + '\n'
            x_index += 7
            breaks -= 1
        str +=" | ".join(x_list[x_index:x_index + remainder]) + '\n'

        return str


class Record:
    def __init__(self, a, t, g, s, y, murl, iid, l):
        self.artist = a
        self.title = t
        self.genres = g
        self.styles = s
        self.year = y
        self.master_url = murl
        self.instance_id = iid
        self.labels = l
        self.reissue_year = 0
        self.reissue = False
        self.decade = self.__decade__(y)

    def __decade__(self, year):
        if year == 0:
            return "n/a"
        else:
            return str(year - (year % 10))


def main(argv):
    master = False
    reissues = False
    from_file = False
    arg_dict = {
        "username": "",
        "token": "",
        "inputfile": "",
        "folder": '0'
    }
    usage = '''           Usage: 
            discogsByStyle.py -u <username> [<-t token>] [-i --ifile filepath] [-m --master] [-r --reissue] [-v --verbose] [-f --folders]'''

    # Error check for proper command line inputs
    if not argv:
        print(usage)
        sys.exit(3)
    try:
        # TODO: argparse instead of getopt
        opts, args = getopt.getopt(argv, 'hu:i:t:frmv', ['username=', 'token=', 'ifile=', 'help', 'reissue', 'master', 'verbose', 'folders'])
    except getopt.GetoptError:
        print('Invalid input.  Enter -h for usage.')
        sys.exit(2)

    if not opts:
        print("Invalid input.  Enter -h for usage.")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h' or opt == '--help' or len(argv) == 1:
            print(usage)
            if opt == '-v' or opt == '--verbose': #refaactor usage to allow for verbose
                print('''
                  
                An authentication token is needed to use this program
                Find a token here: https://www.discogs.com/settings/developers
                You may need to sign in to your Discogs account first
                
                Quickstart: discogsByStyle -u <your username here> -t <your token here>
                    
            Flags and Options:
                -u or --username : your Discogs username should be entered here
                -t or --token    : load collection from Discogs using your authentication token
                -f or --folders  : load collection from particular Discogs folder (use with -u and -t)
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
        elif opt in ['-f', '--folders']: #TODO refactor
            get_folders(arg_dict)

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

    myCollection = Discogs_Collection(arg_dict['username'],arg_dict['token'],arg_dict['inputfile']);

# TODO: make this its own function
    # Obtain collection from Discogs, sort by artist name, then sort genres and styles alphabetically, decades by year

    if master or reissues:
        get_masters(f_collection, arg_dict['token'], reissue_num, reissues, master)

    # User Input
    while True:
        cmd = input("Command: ").lower()
        if cmd == 'k':
            Discogs_Collection.display_keys()
        elif cmd in ['s', 'g', 'a', 'o', 'd']:
            display(f_collection, style_list, genre_list, decade_list, cmd, reissues, master, from_file)
        elif cmd == 'r':
            random_record(f_collection, style_list, genre_list, decade_list)
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
                    NOTE:   not all records in Discogs have year information.  For those records that don't
                            have a year, the year may appear as '0' or 'n/a' 
            r: Return a random record from your collection, with filter options
            e: Export/Save your collection to a file
            u: Update your saved collection with your latest additions/substractions from Discogs
                (You will need to save with command 'e' to save your new collection to a file)
            q: Quit''')
        elif cmd == 'e':
            json_file(f_collection)
            print(f"Saved {f_collection[0]['total']} records to {f_collection[0]['inputfile']}")
        elif cmd == 'u':
            if from_file:
                update_collection(f_collection, arg_dict, genre_list, style_list, decade_list, reissue_num)
            else:
                print("Unable to update.  Please load a collection file")
                continue
        else:
            print("Invalid command.  Enter -h for help")

def _overview_display(x_list, x_stats, x_all, coll):
    # Handles text formatting for the overview option (will print style, genre and decade lists in same format)
    for x in x_list:
        num = x_stats.count(x)
        t = (x, num)
        x_all.append(t)
    x_all.sort(key=lambda x: x[1])
    for i in range(len(x_all)):
        print(str(x_all[i][0]) + "." * (40 - len(x_all[i][0])), end="")
        print("{:>4} --- {:>5.2f} %".format(x_all[i][1], (100 * (x_all[i][1] / coll[0]['total']))))

# TODO: move all terminal/console display functions to new file
def display(coll, s_list, g_list, d_list, c, r, m, ff):

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
            print("\nUsage: Enter a key. For list of keys, Press k\nPress q to quit, Press m to return to main menu\n\n"
                  "Output legend:\n[#]. [Artist] - [Title] ([Release Date])\n<IF A REISSUE (R): [Reissue Release Date]>"
                  "\n    Styles: [Styles]\n    Genres: [Genres]\n"
                  "Most accurate date information only available if collection loaded with master release date")
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
            file_name = json_file(coll)
            print(f"Saved {coll[0]['total']} records to {file_name}.json")
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
                    print(f"Saved {coll[0]['total']} records to {coll[0]['inputfile']}")
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

    for record in coll[1]:
        if record.reissue and (r or m or ff):
            zero_year_check = str(record.reissue_year)
            if zero_year_check == '0':
                zero_year_check = "n/a"
            r_str = "\n    (R): " + zero_year_check
        else:
            r_str = ""

        if c == 'a' or (c == 'd' and d_opt in record.decade):
            print(f"{count + 1}. {record.artist} - {record.title} ({record.year}){r_str}\n\t" +
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
            print(". Percentage of Collection = {0:.2f} %".format(100 * count/coll[0]['total']))
        else:
            print("")
    else:
        # Output formatting for 'o' command
        style_stats.sort()
        genre_stats.sort()
        decade_stats.sort()

        # Counts the number of occurrences of a particular style/genre/decade and creates a tuple, which is then added
        # to a list of styles.  That list of (style, count) tuples is sorted based on the count, and then printed

        print(" " * 19 + "TOTAL STYLES\n" + ("-" * 56))
        _overview_display(s_list, style_stats, all_styles, coll)
        print("-" * 56 + "\n" + " " * 19 + "TOTAL GENRES\n" + ("-" * 56))
        _overview_display(g_list, genre_stats, all_genres, coll)
        print("-" * 56 + "\n" + " " * 18 + "TOTAL DECADES\n" + ("-" * 56))
        _overview_display(d_list, decade_stats, all_decades, coll)
        print("-" * 56 + f"\nTotal: {count}")
        if not coll[0]['master_data']:
            print("For most accurate Total Decade data, run program with -m")





def get_folders(arg_d):
    while True:
        try:
            folder_ids = []
            folder_opt = -1
            url = f"https://api.discogs.com/users/{arg_d['username']}/collection/folders?token={arg_d['token']}"
            response = requests.get(url)
            _error_check(response)
            folder_dict = response.json()
            for folder in folder_dict['folders']:
                folder_ids.append(str(folder['id']))
            while folder_opt not in folder_ids:
                print("Choose Folder:")
                for folder in folder_dict['folders']:
                    print(f"For {folder['name']}, enter {folder['id']}")
                folder_opt = input("Folder number: ")
                if folder_opt == 'h':
                    print("Select your folder from the options above.  If you do not see the folder you are looking "
                          "for, try running this program with a token.")
                elif folder_opt == 'q':
                    sys.exit()
            arg_d['folder'] = folder_opt
            return 0
        except KeyError:
            if not arg_d['username'] or not arg_d['token']:
                arg_d['username'] = input("Enter Username: ")
                arg_d['token'] = input("Enter Token: ")
            else:
                print("Something went wrong.  Exiting")
                sys.exit(4)
        except requests.exceptions.ConnectionError as e:
            print("ConnectionError: No connection established.  Max retries exceeded.\nExiting...")
            sys.exit(4)

def get_masters(coll, token, num_r, r, m): #make this async - individual calls after the main call.

    wait_str = ""
    time_tup = ()

    if r:
        coll[0]['reissue_data'] = True
        coll[0]['master_data'] = False
    elif m:
        coll[0]['master_data'] = True
        coll[0]['reissue_data'] = True

    # Estimated wait time based on number of reissues
    if __name__ == "__main__":
        if r:
            time_tup = divmod(num_r[0], 60)
            wait_str = "reissues'"

        elif m:
            time_tup = divmod(coll[0]['total'], 60)
            wait_str = "all"
        # TODO: do not output this if you are updating a collection
        print(f"Loading {wait_str} master release dates..." +
              "\nEstimated wait time: {} minutes and {} seconds".format(time_tup[0], time_tup[1]))

    # Sleep for a few seconds based on the number of previously made API calls to avoid 429 Response
    start_sleep = int(len(coll[1])/100 + 1)
    time.sleep(start_sleep)
    sleep_time = 1
    count = 1
    blocks = ""
    progress_bar = 5

    for record in coll[1]:
        if not record.reissue:
            if r:
                count += 1
                continue
            elif m:
                pass

        if record.master_url is None:
            count += 1
            continue

        url = record.master_url + "?token=" + token
        try:
            response = requests.get(url)
            _error_check(response)
        except requests.exceptions.ConnectionError:
            print("ConnectionError: Max retries exceeded.  No connection established\nAborting...")
            return

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
        #TODO: do not output this string if you're updating a collection (its inaccurate)
        print("\rLoading {:{pad}d} of {} records - {:20}{:.2f}%"
              .format(count, coll[0]['total'], blocks, (count/coll[0]['total'])*100, pad=len(str(coll[0]['total']))),
              end="")

        if int(100*count/coll[0]['total']) >= progress_bar:
            blocks += chr(9608)
            progress_bar += 5

        time.sleep(sleep_time)
        count += 1
    print()
    return 0


def update_collection(coll, args, g_list, s_list, d_list, re_s):
    to_remove = []

    if not args['username']:
        args['username'] = input("Enter Username: ")

    if not args['token']:
        args['token'] = input("Enter Token: ")

    update_coll = get_discogs(args, False)
    update_coll = format_discogs(args, update_coll, g_list, s_list, d_list, re_s, False)

    # Sorting both collections by instance id to speed up nested for loops later
    coll[1].sort(key=lambda x: x.instance_id)
    update_coll[1].sort(key=lambda x: x.instance_id)

    if not coll[0]['master_data'] or not coll[0]['reissue_data']:
        coll = update_coll
        print("Your collection has been successfully updated")
        return 0
    else:
        for i in range(len(coll[1])):
            for j in range(len(update_coll[1])):
                removed = True
                # If the collection record is still in the update, then the record can be removed from the update
                if coll[1][i].instance_id == update_coll[1][j].instance_id:
                    update_coll[1].remove(update_coll[1][j])
                    removed = False
                    break
                else:
                    pass
            # If the collection record isn't found in the update, then the record has been removed
            if removed:
                to_remove.append(coll[1][i])
        if to_remove:
            print(f"Removing {len(to_remove)} from collection...")
            for record in to_remove:
                for i in range(len(coll[1])):
                    if record.instance_id == coll[1][i].instance_id:
                        coll[1].remove(coll[1][i])
                        break
        else:
            print("No records to remove.")
        # If there are still records in the update, then these are new records to be added to the collection.
        if update_coll[1]:
            # print to screen the records that will be added to the collection
            for i in range(len(update_coll[1])):
                print(f"Adding {update_coll[1][i].artist} - {update_coll[1][i].title} to your collection")
            up = []
            up.append(len(update_coll[1]))
            #TODO: get_masters shouldn't output the normal loading screen when doing an update
            get_masters(update_coll, args['token'], up, False, True)
            print(f"Updated collection with {len(update_coll[1])} new record(s)")
        else:
            print("No new records to add.")

        coll[0]['total'] = update_coll[0]['total']
        coll[0]['date_created'] = time.localtime()
        coll[1].extend(update_coll[1])
        coll[1].sort(key=lambda x: x.artist)

        print("Enter command 'e' to save your updated collection")
        return 0

#TODO: make this a separate file and refactor everything into a Collection object
def random_record(coll, r_s_list, r_g_list, r_d_list):
    if __name__ == "__main__":
        print('''
This will choose a random record from your collection.
To choose any record, enter "-a"
To filter by genre, enter a genre key
Type "-k" for key list
Type "-m" to return to main menu
Type "-q" to quit''')
    while True:
        f_cmd = input("Enter Random Record Filter: ")
        if f_cmd == '-k':
            display_keys(r_s_list, r_g_list, r_d_list)
            f_cmd = ""
        elif f_cmd == '-a':
            i = random.randint(0, len(coll[1]))
            print(f"{coll[1][i].artist} - {coll[1][i].title}")
            #TODO: call to tkinter function to popup window
            return
        elif f_cmd == '-q':
            sys.exit()
        elif f_cmd == '-m':
            return
        else:
            #TODO: allow different filters (style and decade too)
            search_list = []
            for r in coll[1]:
                # TODO: debug this to see if records are being added more than once because of the r.styles loop
                for g in r.genres:
                    if f_cmd.lower() == g.lower():
                        search_list.append(r)
                for s in r.styles:
                    if f_cmd.lower() == s.lower() and r not in search_list:
                        search_list.append(r)
            i = random.randint(0, len(search_list))
            try:
                print(f"{search_list[i].artist} - {search_list[i].title}")
                print(f"G: {search_list[i].genres} - S: {search_list[i].styles}")
            except IndexError:
                print("No records found")
                continue
            return


if __name__ == "__main__":
    main(sys.argv[1:])
