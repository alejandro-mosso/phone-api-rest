from pandas import read_csv
from phonenumbers import phonenumberutil, prefix, PhoneNumber
from phonenumbers.util import U_PLUS
from phonenumbers import is_valid_number, parse
from multiprocessing import Process, Queue
from streamz import Stream
from math import ceil
from itertools import islice

try:
    from phonenumbers.geodata import GEOCODE_DATA, GEOCODE_LONGEST_PREFIX
    from phonenumbers.geodata.locale import LOCALE_DATA
except ImportError:  # pragma no cover
    import os
    import sys
    if (os.path.basename(sys.argv[0]) == "buildmetadatafromxml.py" or
        os.path.basename(sys.argv[0]) == "buildprefixdata.py"):
        GEOCODE_DATA = {'1': {'en': ('United States')}}
        GEOCODE_LONGEST_PREFIX = 1
        LOCALE_DATA = {'US': {'en': ('United States')}}
    else:
        raise

states = {"AL": "Alabama",          "AK": "Alaska",         "AZ": "Arizona",
          "AR": "Arkansas",         "CA": "California",     "CO": "Colorado",
          "CT": "Connecticut",      "DE": "Delaware",       "FL": "Florida",
          "GA": "Georgia",          "HI": "Hawaii",         "ID": "Idaho",
          "IL": "Illinois",         "IN": "Indiana",        "IA": "Iowa",
          "KS": "Kansas",           "KY": "Kentucky",       "LA": "Louisiana",
          "ME": "Maine",            "MD": "Maryland",       "MA": "Massachusetts",
          "MI": "Michigan",         "MN": "Minnesota",      "MS": "Mississippi",
          "MO": "Missouri",         "MT": "Montana",        "NE": "Nebraska",
          "NV": "Nevada",           "NH": "New Hampshire",   "NJ": "New Jersey",
          "NM": "New Mexico",       "NY": "New York",       "NC": "North Carolina",
          "ND": "North Dakota",     "OH": "Ohio",           "OK": "Oklahoma",
          "OR": "Oregon",           "PA": "Pennsylvania",   "RI": "Rhode Island",
          "SC": "South Carolina",   "SD": "South Dakota",   "TN": "Tennessee",
          "TX": "Texas",            "UT": "Utah",           "VT": "Vermont",
          "VA": "Virginia",         "WA": "Washington State",
          "WV": "West Virginia",    "WI": "Wisconsin",      "WY": "Wyoming",
          "AB": "Alberta",          "BC": "British Columbia",
          "MB": "Manitoba",         "NB": "New Brunswick",  "NL": "Newfoundland and Labrador",
          "NT": "Northwest Territories",                    "NS": "Nova Scotia",
          "NU": "Nunavut",          "ON": "Ontario",        "PE": "Nova Scotia/Prince Edward Island",
          "QC": "Quebec",           "SK": "Saskatchewan",   "YT": "Yukon"}


def prefix_description_for_number(data, longest_prefix, numobj, lang, script=None, region=None):
    name_list = []

    e164_num = phonenumberutil.format_number(numobj, phonenumberutil.PhoneNumberFormat.E164)
    if not e164_num.startswith(U_PLUS):  # pragma no cover
        # Can only hit this arm if there's an internal error in the rest of
        # the library
        raise Exception("Expect E164 number to start with +")

    for prefix_len in range(5, 3, -1):
        p = e164_num[1:(1 + prefix_len)]
        if p in data:
            # This prefix is present in the geocoding data, as a dictionary
            # mapping language info to location name.
            name = prefix._find_lang(data[p], lang, script, region)
            if name is not None:
                # return name
                name_list.append(name)
            # else:
                # return U_EMPTY_STRING
                # name_list.append(U_EMPTY_STRING)
    # return U_EMPTY_STRING
    # name_list.append(U_EMPTY_STRING)
    return name_list


def get_location_for_number(phone_p):
    location_arr = prefix_description_for_number(GEOCODE_DATA, GEOCODE_LONGEST_PREFIX, phone_p, 'en', None, None)
    loc: str = 'n/a'
    state: str = 'n/a'
    if len(location_arr) == 1:
        loc = location_arr[0]
        state = location_arr[0]
        location_splitted = state.split(', ')
        if len(location_splitted) > 1:
            state = states[location_splitted[len(location_splitted)-1]]
            if not state:
                state = location_splitted[len(location_splitted)-1]
    elif len(location_arr) > 1:
        loc = location_arr[0]
        state = location_arr[len(location_arr)-1]

    return [loc, state]


def set_location(tup):
    row = tup[1]
    phone: PhoneNumber = parse('+1 ' + row.numbers, None)
    location_arr = get_location_for_number(phone)

    row.state = location_arr[1]

    return row


def reformat(tup):
    row = tup[1]
    phone: PhoneNumber = parse('+1 ' + row.numbers, None)
    location_arr = get_location_for_number(phone)
    is_valid = is_valid_number(phone) # len(location_arr) > 0 #

    row.is_valid = is_valid
    row.location = location_arr[0]
    # row.state = location_arr[1]

    return row


def filter_number(row, in_number):
    phone = parse(in_number, None)
    location = get_location_for_number(phone)
    return row.state == location[1]


def get_data_frame(row):
    return row


def print_dataframe(row: object, q: Queue) -> object:
    q.put(row)
    return row


def emit_iterator(src: Stream, iter, slice_size, index):
    src.emit(islice(iter, index*slice_size, (index+1)*slice_size))


# input_number = "+1 (310) 123-1234"
def locate_nearest_numbers(input_number, csv_location):
    result = []
    queue = Queue()
    running_cores: int = 8
    data_frame = read_csv(csv_location)
    data_frame["state"] = None

    iter1 = data_frame.iterrows()
    partition_size = ceil(len(data_frame.index)/running_cores)

    processes = []

    for i in range(running_cores):
        source = Stream(asynchronous=True)
        source.map(get_data_frame).flatten().\
            map(set_location).filter(filter_number, input_number).\
            sink(print_dataframe, queue)
        process = Process(target=emit_iterator, args=(source, iter1, partition_size, i))
        processes.append(process)
        process.start()

    while 1:
        is_running = any(p.is_alive() for p in processes)
        while not queue.empty():
            result.append(queue.get())
        if not is_running:
            break

    for p in processes:
        p.join()

    return result


def reformat_numbers(csv_location):
    result = []
    queue = Queue()
    running_cores: int = 8
    data_frame = read_csv(csv_location)
    data_frame["location"] = None
    data_frame["is_valid"] = None
    # data_frame["state"] = None

    iter1 = data_frame.iterrows()
    partition_size = ceil(len(data_frame.index)/running_cores)

    processes = []

    for i in range(running_cores):
        source = Stream(asynchronous=True)
        source.map(get_data_frame).flatten().\
            map(reformat).\
            sink(print_dataframe, queue)
        process = Process(target=emit_iterator, args=(source, iter1, partition_size, i))
        processes.append(process)
        process.start()

    while 1:
        is_running = any(p.is_alive() for p in processes)
        while not queue.empty():
            result.append(queue.get())
        if not is_running:
            break

    for p in processes:
        p.join()

    return result


if __name__ == '__main__':
    print(reformat_numbers('/home/amosso/Downloads/numbers_small.csv'))
