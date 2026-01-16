import csv
import sys
import requests
import re


def process_row(current_row):
    direct_xml_url = current_row["DirectXml"].strip()
    institution = current_row["Institution"].strip()
    guess_url = current_row["Guess"].strip()

    ascii_institution = re.sub(r'[^A-Za-z0-9]+', '', institution)

    print(f"================= {institution} =================")
    print(f"directXml: {direct_xml_url}, guess: {guess_url}")

    direct_output = None
    guess_output = None
    try:
        url = direct_xml_url
        direct_response = requests.get(url, timeout=30)
        direct_output = direct_response.text
        print(f"-----there is direct output")
    except Exception as e:
        print(f"*****An error occurred with direct {direct_xml_url}: {e.__class__.__name__}")

    try:
        url = guess_url
        guess_response = requests.get(url, timeout=30)
        guess_output = guess_response.text
        print(f"-----there is also guess output")
    except Exception as e:
        print(f"*****An error occurred with guess {guess_url}: {e.__class__.__name__}")

    if direct_output is not None:
        with open(f"{ascii_institution}_direct.txt", "w") as d:
            print(f"Look for file, {ascii_institution}_direct.txt")
            print(direct_output, file=d)

            if guess_output is not None:
                if guess_output != direct_output:
                    with open(f"{ascii_institution}_guess.txt", "w") as g:
                        print(f"Look for file, {ascii_institution}_guess.txt")
                        print(guess_output, file=g)
                        print("Guess output differs from direct")
                else:
                    print("Guess output is the same as direct")


def process_file():
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        rows_list = list(csv_reader)

        if csv_reader.fieldnames:
            for my_index, (row) in enumerate(rows_list):
                process_row(row)

        else:
            print("No headers found in the CSV file.")
            exit(1)


if __name__ == "__main__":
    search_term = 'asthma'  # default
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        print(f"Input CSV: {csv_file}")
        if len(sys.argv) > 2:
            search_term = sys.argv[2]
            print(f"Search term: {search_term}")
            if search_term == 'None':
                search_term = None
        process_file()
    else:
        print("No CSV provided.")
        print(f"Usage: {sys.argv[0]} <csv-file>")
        exit(1)
