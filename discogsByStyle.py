import requests
import sys


class Record:
    def __init__(self,a,t,g,s):
        self.artist = a
        self.title = t
        self.genres = g
        self.styles = s



def main():
    genre_list = []
    style_list = []
    coll_size = 0

    if len(sys.argv) != 3 or "-h" in sys.argv:
        print("Usage: discogsByStyle.py <username> <token>\nFind a token here: discogs.com/settings/developers")
        sys.exit()

    print("\t***********DISCOGS BY STYLE***********\n" +
    "\t* This app will sort your discogs    *\n" +
    "\t* collection by style or genre.      *\n" +
    "\t* Enter '-h' at anytime for help.    *\n" +
    "\t**************************************\n\nLoading your Collection now.  This may take a few seconds...")

    collection = get_vinyl(sys.argv)
    f_collection = format_out(collection, genre_list, style_list)
    f_collection.sort(key=lambda x: x.artist)
    coll_size = len(f_collection)
    genre_list.sort()
    style_list.sort()

    while True:
        cmd = input("Command: ")
        if cmd.lower() == 'k':
            print(f"Style Keys: {' | '.join(style_list)}\n")
            print(f"Genre Keys: {' | '.join(genre_list)}\n")
        elif cmd.lower() == 's' or cmd.lower() == 'g':
            display(f_collection, style_list, genre_list, cmd, coll_size)
        elif cmd.lower() == 'q':
            sys.exit()
        elif cmd.lower() == '-h':
            print("Usage:\nk: print style and genre keys\ns: lookup by style\ng: lookup by genre\nq: quit")
        else:
            print("Invalid command.  Enter -h for help")


def format_out(coll, g_list, s_list):
    records = []

    for i in range(len(coll)):
        for j in range(len(coll[i]['releases'])):
            title = coll[i]['releases'][j]['basic_information']['title']
            artist = coll[i]['releases'][j]['basic_information']['artists'][0]['name']
            genres = coll[i]['releases'][j]['basic_information']['genres']
            styles = coll[i]['releases'][j]['basic_information']['styles']

            rec = Record(artist, title, genres, styles)
            records.append(rec)

            for s in styles:
                if not(s in s_list):
                    s_list.append(s)
            for g in genres:
                if not(g in g_list):
                    g_list.append(g)

    return records


def display(coll, s_list, g_list, c, size):
    _opt = ""
    count = 0

    if c == 's':
        sort_type = s_list
        sort_str = "Style"
    else:
        sort_type = g_list
        sort_str = "Genre"

    # TODO: add option to sort by release year
    while not (_opt in sort_type):
        _opt = input(f"Choose {sort_str}: ")

        if _opt.lower() == '-h':
            _opt = input("Usage: Enter a key. For list of keys, Press k. Input a key or press enter to continue. ")

        if _opt.lower() == 'k':
            if c == 's':
                print(f" Styles: {' | '.join(s_list)}")
            else:
                print(f" Genres: {' | '.join(g_list)}")
        else:
            pass

    for record in coll:
        if c == 's' and _opt in record.styles:
            print(f"{count + 1}. {record.artist} - {record.title} --- ({' | '.join(record.styles)})")
            count += 1
        elif c == 'g' and _opt in record.genres:
            print(f"{count + 1}. {record.artist} - {record.title} --- ({' | '.join(record.genres)})")
            count += 1
        else:
            pass

    print("---------------------------------------------------------------")
    print("Total: {0}. Percentage of Collection = {1:.2f} %".format(count, (100*count/size)))


def error_check(res):
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