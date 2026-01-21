import csv
import sys
import requests
import re


def dump_content(content, filename, label):
    with open(filename, "w") as g:
        prinfo(f"Writing '{label}' file to {filename}")
        print(content, file=g)


def curl_for_output(url, label):
    try:
        url = url
        url_response = requests.get(url, timeout=30)
        url_output = url_response.text
        prinfo(f"Got '{label}' output")
        return url_output
    except Exception as e:
        prerror(f"No '{label}' output. {e.__class__.__name__}")
        return None


def print_helper(content, double, label):
    post = label+label if double else ''
    print(f"{label} {content} {post}")


def preveryemphatic(content, double):
    print("-----------------------------------------------------------------------------")
    premphatic(content, double)
    print("-----------------------------------------------------------------------------")


def premphatic(content, double):
    print_helper(content, double, '================')


def precial(content, double):
    print_helper(content, double, '=++=++=++=++=++')


def prerror(content):
    print_helper(content, False, '*****')


def prinfo(content):
    print_helper(content, False, '-----')


def extract_count(content, regex_match, regex_extract):
    result = None  # burden of proof
    if re.match(regex_match, content):
        # looks like need to account for earlier stuff, but not later
        result = re.findall(regex_extract, content)[0]
    return result


def extract_query(content):
    result = None  # burden of proof

    if re.match(r'(?s).*aggregate-query', content):
        # looks like need to account for earlier stuff, but not later
        result = re.findall(r'.*aggregate-query.*?(http.*)<', content)[0]
        result = re.sub(r'&amp;', '&', result)

    return result


def report_count(institution, content, label, regex_match, regex_extract):
    count = extract_count(content, regex_match, regex_extract)
    if count is None:
        prerror(f"NO COUNT from {institution} via '{label}'")
    else:
        precial(f"Got count of {count} from {institution} via '{label}'", True)


def process_row(current_row):
    search_term = "" if l_search_term is None else l_search_term
    bootstrap_xml_url = current_row["BootstrapXml"].strip()
    institution = current_row["Institution"].strip()
    core_url = current_row["Guess"].strip()
    guess_query_url = f"{core_url}{search_term}"

    ascii_institution = re.sub(r"[^A-Za-z0-9]+", "", institution)

    preveryemphatic(institution, True)
    premphatic(f"bootstrap url: {bootstrap_xml_url}", False)
    premphatic(f"guess query url: {guess_query_url}", False)

    bootstrap_output = curl_for_output(bootstrap_xml_url, l_bootstrap)
    bs_query_output = None

    if bootstrap_output is not None:
        dump_content(bootstrap_output, f"outputFiles/{ascii_institution}_bootstrap.xml", l_bootstrap)
        bs_query_url = extract_query(bootstrap_output)
        if bs_query_url is None:
            prerror(f"No bs_query from [{l_bootstrap} {bootstrap_xml_url}]")
        else:
            bs_query_url += search_term
            prinfo(f"Got bs_query '{bs_query_url}'")

            bs_query_output = curl_for_output(bs_query_url, l_bs_query)
            if bs_query_output is not None:
                dump_content(bs_query_output, f"outputFiles/{ascii_institution}_bsQuery.txt", l_bs_query)
                report_count(ascii_institution, bs_query_output, l_bs_query, l_aggregation_match, l_aggregation_extract)

        guess_query_output = curl_for_output(guess_query_url, l_guess_query)
        if guess_query_output is not None:
            comparison = 'is the same as' if guess_query_output == bs_query_output else 'differs from'
            precial(f"Output from 'guess' {comparison} that of bs_query", True)

            if comparison == 'differs from':
                regex_match = current_row["ScrapeRegexM"]
                regex_extract = current_row["ScrapeRegexE"]
                if regex_match is None or regex_extract is None:
                    regex_match = l_aggregation_match
                    regex_extract = l_aggregation_extract
                    prinfo(f"Using regexes: '{regex_match}' and '{regex_extract}'")
                else:
                    regex_match = regex_match.strip()
                    regex_extract = regex_extract.strip()
                    prinfo(f"NB: Using regexes -- '{regex_match}' and '{regex_extract}' -- which may match post-AJAX content, but not necessarily the contents returned by curl")

                report_count(ascii_institution, guess_query_output, l_guess_query, regex_match, regex_extract)


def process_file():
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        rows_list = list(csv_reader)

        if csv_reader.fieldnames:
            for my_index, (row) in enumerate(rows_list):
                process_row(row)
                # print(f"==================================Current index is {my_index}")
                # if my_index == 1:
                #     break

        else:
            print("No headers found in the CSV file.")
            exit(1)


if __name__ == "__main__":
    l_search_term = "asthma"  # default
    l_bootstrap = "bootstrap"
    l_guess_query = "guess"
    l_bs_query = "bs_query"
    l_aggregation_match = r"(?s).*aggregation-result"
    l_aggregation_extract = r"(?s).*<count>(\d+)<"


if len(sys.argv) > 1:
    csv_file = sys.argv[1]
    prinfo(f"Input CSV: {csv_file}")
    if len(sys.argv) > 2:
        l_search_term = sys.argv[2]
        prinfo(f"Search term: {l_search_term}")
        if l_search_term == "None":
            l_search_term = None
        process_file()
    else:
        prerror("No CSV provided.")
        prerror(f"Usage: {sys.argv[0]} <csv-file>")
        exit(1)
