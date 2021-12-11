import re
import json
import random
import requests
from bs4 import BeautifulSoup
from  audiorecorder import record_audio, read_audio




WIT_API_ENDPOINT = 'https://api.wit.ai/speech'
BOOK_API_ENDPOINT = 'https://www.goodreads.com/genres/'


WIT_ACCESS_TOKEN = 'IXOH5HPPECPC2KIHJ6Q7MQAOKXFIFRRD' 

CATEGORIES = json.loads('[{"genre":"Art","category":"hobby"},{"genre":"Biography", "category":"biography"},{"genre":"Business","category":"entrepreneurship"},{"genre":"Children-s","category":"children"},{"genre":"Classics","category":"classic"},{"genre":"Cookbooks","category":"cooking"},{"genre":"Crime","category":"suspense"},{"genre":"Fantasy","category":"fantasy"},{"genre":"Fiction","category":"fantasy"},{"genre":"History","category":"history"},{"genre":"Horror","category":"fantasy"},{"genre":"Music","category":"music"},{"genre":"Mystery","category":"fantasy"},{"genre":"Paranormal","category":"fantasy"},{"genre":"Philosophy","category":"psychology"},{"genre":"Romance","category":"romance"},{"genre":"love","category":"romance"},{"genre":"Science","category":"hobby"},{"genre":"ScienceFiction","category":"fantasy"},{"genre":"Self-Help","category":"psychology"},{"genre":"Suspense","category":"suspense"},{"genre":"Spirituality","category":"psychology"},{"genre":"Sports","category":"hobby"},{"genre":"Thriller","category":"suspense"},{"genre":"Travel","category":"hobby"},{"genre":"Young Adult","category":"teen"}]')

def recognize_speech(filename, audio_length):
    
    # recond an audio file for a given duration in seconds
    record_audio(audio_length, filename)

    audio = read_audio(filename)

    headers = {'authorization': 'Bearer ' + WIT_ACCESS_TOKEN,
               'Content-Type': 'audio/wav'}

    resp = requests.post(WIT_API_ENDPOINT, headers = headers,
                         data = audio)

    #print(data)
    return json.loads(resp.content)
 
def analyze_speech(recorded_speech):
    book_types = ""
    searched_book_type = ""
    if 'book_keywords:book_keywords' in recorded_speech['entities']:
        book_types = recorded_speech['entities']['book_keywords:book_keywords']

    if book_types:
       for key in book_types:
           searched_book_type = key['value']


    return [
        category['genre']
        for category in CATEGORIES
        if searched_book_type == category['category']
    ]   
    
def get_book_recommendations(genre):
    book_site_response = requests.get(BOOK_API_ENDPOINT + genre)
    print('called url: ', BOOK_API_ENDPOINT + genre) 
    soup = BeautifulSoup(book_site_response.text, "html.parser")
    book_entries = soup.find_all("div", class_="bookBox")

    for book in book_entries:
        book_id = book.find("div", class_="coverWrapper")['id']
        #print("book id:", book_id)
        soup_string = str(book)
        matcher = re.search(book_id + '\'\),\s(.*)(<h2>.*div>)', soup_string)
        innerBookHtml = matcher.group(2)
        #print(innerBookHtml)
        book_element = BeautifulSoup(innerBookHtml.replace(r"\"", '"').replace(r"\/", "/"), "html.parser")
        book_title = book_element.find("a", class_="bookTitle").text
        print("Title: ", book_title)
        book_link = book_element.find("a", class_="bookTitle")['href']
        print("Link: ", book_link)
        book_author = book_element.find("a", class_="authorName").text
        print("Author: ", book_author)
        print("**************************************")        

if __name__ == "__main__":
    speech =  recognize_speech('speech.wav', 4)
    print("\nRecognized speech: {}".format(speech['text']))

    possible_genres = analyze_speech(speech)
    if possible_genres:
       print("I have found something for you:", possible_genres)
       if len(possible_genres) > 1:
           genre_param = random.choice(possible_genres) 
           print("picked a random genre from multiple categories:", genre_param) 
       else:
           genre_param = possible_genres[0]     
       get_book_recommendations(genre_param)      
    else:
     print("Sorry, I didn't find anything") 
