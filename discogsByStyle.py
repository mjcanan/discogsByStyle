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

    if len(sys.argv) != 3 or "-h" in sys.argv:
        print("Usage: discogsByStyle.py <username> <token>\nFind a token here: discogs.com/settings/developers")
        sys.exit()

    collection = get_vinyl(sys.argv)

    f_collection = format_out(collection, genre_list, style_list)
    f_collection.sort(key=lambda x: x.artist)

    display_style(f_collection, style_list, genre_list)


def format_out(coll, g_list, s_list):
    # TODO: implement sort by style
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


def display_style(coll, s_list, g_list):
    style_opt = ""
    count = 0
    s_list.sort()
    g_list.sort()

    print(f"All Styles: {', '.join(s_list)}")
    print(f"\nAll Genres: {', '.join(g_list)}")
    # TODO: add option to sort by genre
    # TODO: add option to sort by release year
    while True:
        while not (style_opt in s_list):
            style_opt = input("Choose style: ")

        for record in coll:
            if style_opt in record.styles:
                print(f"{count + 1}. {record.artist} - {record.title} --- ({', '.join(record.styles)})")
                count += 1
        print(f"Total records of that style: {count}")
        to_close = input("Press Q to Quit, Press Enter to Continue: ")
        if to_close.lower() == 'q':
            sys.exit()
        else:
            style_opt = ""
            count = 0


def error_check(res):
    if not(res.status_code == 200):
        print("An Error Occurred.  Please Try Again.")
        print(f"Code {res.status_code}: {res.reason}.")
        sys.exit()


def get_vinyl(arg_list):
    # TODO: allow for selection of private folders - current implementation only selects Uncategorized folder
    col_list = []
    url = ("https://api.discogs.com/users/" + arg_list[1] + "/collection/folders/1/releases?token=" + arg_list[2]
           + "&per_page=100")
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