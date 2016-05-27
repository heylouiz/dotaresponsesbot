#!/bin/python
""" Module that find the best dota 2 response from a givem text"""

import json
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://dota2.gamepedia.com/'
API_URL = 'api.php?action=query&list=categorymembers&cmlimit=max' +  \
                                                   '&cmprop=title' + \
                                                   '&format=json' +  \
                                                   '&cmtitle=Category:'
END_URL = 'Lists_of_responses'


def fetch_response_pages():
    """Fetches all available response pages from the Dota Wiki"""
    response_pages = []
    category_json = requests.get(BASE_URL + API_URL + END_URL).json()
    for category in category_json["query"]["categorymembers"]:
        if not 'Announcer' in category["title"]: # Exclude announcer packs
            response_pages.append(BASE_URL + category["title"].replace(" ", "_"))
    return response_pages

def parse_page(page):
    """Returns a page object parsed with BeautifulSoup"""
    return BeautifulSoup(requests.get(page).text, 'html.parser')

def parse_html(html):
    """Returns a html object parsed with BeautifulSoup"""
    return BeautifulSoup(html, 'html.parser')

def create_response_dict(response_pages):
    """Create and returns a dict with all hero responses.
       Example Dict format: { "Axe_Responses": [{"text": "Not so fast!",
                                                "url": "http://hydra-media.cursecdn.com/"
                                                       "dota2.gamepedia.com/d/d2/"
                                                       "Axe_blinkcull_01.mp3"}]}
    """
    response_dict = {}
    for page in response_pages:
        page_name = page.split("/")[-1]
        if page_name.find("Abyssal") >= 0: # Exclude Abyssal Warlord
            pass

        soup = parse_page(page) # BeautifulSoup object, holding a parsed page

        hero_responses = []
        for li_obj in soup.find_all("li"): # Return all <li> in the page
            a_url = li_obj.find("a", class_="sm2_button")
            if a_url:
                url = a_url.get("href")
                text = li_obj.get_text().replace(a_url.string, "").strip()
                if li_obj.find("span", id="tooltip"):
                    try:
                        text = text.split(" ", 1)[1]
                    except IndexError:
                        pass
                hero_responses.append({"text": text, "url": url})
        response_dict[page_name] = hero_responses
    return response_dict

def load_response_json(filename):
    """Load a previous created dict from a file"""
    try:
        with open(filename, "r") as response_json:
            response_dict = json.load(response_json)
    except IOError:
        print("Cannot open {}".format(filename))
        return {}

    return response_dict

def matched_strings(string1, string2):
    """Return the number of matched words between two strings"""
    number_of_matches = 0
    for string in string1.split(" "):
        if re.search(r'\b{}\b'.format(string.lower()), string2.lower()) != None:
            number_of_matches += 1
    return number_of_matches


def find_best_response(query, responses_dict, specific_hero=None):
    """Find the best response from a given query"""
    last_matched = 0
    best_match = -1
    hero_match = ""
    for hero, responses in responses_dict.items():
        if specific_hero != None:
            if hero.lower().find(specific_hero.lower()) < 0:
                continue
        for idx, response in enumerate(responses):
            matched = matched_strings(query, response["text"])
            if matched > last_matched:
                best_match = idx
                hero_match = hero
                last_matched = matched
    if hero_match == "" or best_match == -1:
        return "", {}
    else:
        return hero_match, responses_dict[hero_match][best_match]

def find_all_responses(query, responses_dict, specific_hero=None):
    all_responses = dict()
    for hero, responses in responses_dict.items():
        hero_responses = list() # Clear responses
        if specific_hero != None:
            if hero.lower().find(specific_hero.lower()) < 0:
                continue
        for response in responses:
            if response["text"].lower().find(query.lower()) >= 0:
                hero_responses.append(response)
        if len(hero_responses) > 0:
            all_responses[hero.replace("_responses", "")] = hero_responses
    return all_responses

if __name__ == "__main__":
    PAGES = fetch_response_pages()
    RESP_DICT = create_response_dict(PAGES)
    json.dump(RESP_DICT, open("newresponses.json", 'w'))
    #resp_dict = load_response_json("responses.json")
    #best_hero, best_response = find_best_response("first blood", resp_dict, "axe")
    #print(find_all_responses("first blood", resp_dict))
    #print(best_hero)
    #print(best_response)

