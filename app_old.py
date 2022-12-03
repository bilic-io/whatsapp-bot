from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import json
import datetime
import random
import re

app = Flask(__name__)


@app.route('/bot', methods=['POST'])
def bot():
    # add webhook logic here and return a response
    incoming_msg = request.values.get('Body', '').lower()

    resp = MessagingResponse()
    msg = resp.message()
    responded = False

    response1 = """
*Hi! I am the Quarantine Bot* 👋
Let's be friends 😉
You can give me the following commands:
~  *'quote'*: ```Hear an inspirational quote to start your day!```🚀

~  *'cat'*:   Who doesn't love cat pictures? 🐈

~  *'dog'*:   Don't worry, we have dogs too! dog🐕

~  *'meme'*:  The top memes of today, fresh from r/memes. 👻

~  *'news'*:  Latest news from around the world. 📰

~  *'recipe'*:  Searches Allrecipes.com for the best recommended recipes. 🍴

~  *'recipe <query>'*:  Searches Allrecipes.com for the best recipes based on your query. 🧙

~  *'get recipe'*:  Run this after the 'recipe' or 'recipe <query>' command to fetch your recipes! 

~  *'statistics <country>'*:  Show the latest COVID19 statistics for each country.

~  *'statistics <prefix>'*:  Show the latest COVID19 statistics for all countries starting with that prefix. 

~  *'developer'*:   Know the developer.
"""

    # will find and match either hello or hallo in a message
    if re.search('h[ae]llo', incoming_msg):
        msg.body(response1)
        responded = True

    elif re.search('quote', incoming_msg):  # will find and match quote in a sentence
        # return a quote
        r = requests.get('https://api.quotable.io/random')
        if r.status_code == 200:
            data = r.json()
            quote = f'{data["content"]} ({data["author"]})'
        else:
            quote = 'I could not retrieve a quote at this time, sorry.'
        msg.body(quote)
        responded = True

    elif re.search('cat|pic', incoming_msg):  # will find and match cat or pic
        # return a cat pic
        msg.media('https://cataas.com/cat')
        responded = True

    elif re.search('dog', incoming_msg):
        # return a dog pic
        r = requests.get('https://dog.ceo/api/breeds/image/random')
        data = r.json()
        msg.media(data['message'])
        responded = True

    elif re.search('score', incoming_msg):

        # search for recipe based on user input (if empty, return featured recipes)
        search_text = incoming_msg.replace('score', '')
        search_text = search_text.strip()

        # Get wallet bilic Score

        # print(search_text)

        # data = json.dumps({'searchText': search_text})

        # testing = "testing this shit out {}, recipes.".format(search_text)

        api_url = "https://api.bilic.co.uk/rating/address/{}".format(search_text)

        # Set the request headers
        headers = {
            "Content-Type": "application/json"
        }


        # Make a GET request to the API
        # response = requests.get(api_url)

        # call bilic api

        # print(api_url)
        
        # Check the response status code

        r = requests.get(api_url, headers)

        response = requests.get(api_url)

        if response.status_code == 200:
        # Print the response data
            print(response.json())
        else:
            # Print an error message
            print(f"Failed to retrieve data from the API. Status code: {response.status_code}")

        # if r.status_code == 200:
        #     data = r.json()
        #     print(data)

        #     quote = f'{data["bilic_rating"]} ({data["nbr_account_age_days"]})'
        # else:
        #     quote = 'I could not retrieve a quote at this time, sorry.'

        # msg.body(quote)
        responded = True

    elif re.search('recipe', incoming_msg):

        # search for recipe based on user input (if empty, return featured recipes)
        search_text = incoming_msg.replace('recipe', '')
        search_text = search_text.strip()

        data = json.dumps({'searchText': search_text})

        result = ''
        # updates the Apify task input with user's search query
        r = requests.put(
            'https://api.apify.com/v2/actor-tasks/o7PTf4BDcHhQbG7a2/input?token=qTt3H59g5qoWzesLWXeBKhsXu&ui=1',
            data=data, headers={"content-type": "application/json"})
            
        if r.status_code != 200:
            result = 'Sorry, I cannot search for recipes at this time.'

        # runs task to scrape Allrecipes for the top 5 search results
        r = requests.post(
            'https://api.apify.com/v2/actor-tasks/o7PTf4BDcHhQbG7a2/runs?token=qTt3H59g5qoWzesLWXeBKhsXu&ui=1')
        if r.status_code != 201:
            result = 'Sorry, I cannot search Allrecipes.com at this time.'

        if not result:
            result = "I am searching Allrecipes.com for the best {} recipes.".format(
                search_text)

            result += "\nPlease wait for a few moments before typing 'get recipe' to get your recipes!"
        msg.body(result)
        responded = True

    elif incoming_msg == 'get recipe':
        # get the last run details
        r = requests.get(
            'https://api.apify.com/v2/actor-tasks/o7PTf4BDcHhQbG7a2/runs/last?token=qTt3H59g5qoWzesLWXeBKhsXu')

        if r.status_code == 200:
            data = r.json()

            # check if last run has succeeded or is still running
            if data['data']['status'] == "RUNNING":
                result = 'Sorry, your previous query is still running.'
                result += "\nPlease wait for a few moments before typing 'get recipe' to get your recipes!"

            elif data['data']['status'] == "SUCCEEDED":

                # get the last run dataset items
                r = requests.get(
                    'https://api.apify.com/v2/actor-tasks/o7PTf4BDcHhQbG7a2/runs/last/dataset/items?token=qTt3H59g5qoWzesLWXeBKhsXu')
                data = r.json()

                if data:
                    result = ''

                    for recipe_data in data:
                        url = recipe_data['url']
                        name = recipe_data['name']
                        rating = recipe_data['rating']
                        rating_count = recipe_data['ratingcount']
                        prep = recipe_data['prep']
                        cook = recipe_data['cook']
                        ready_in = recipe_data['ready in']
                        calories = recipe_data['calories']

                        result += """
*{}*
_{} calories_
Rating: {:.2f} ({} ratings)
Prep: {}
Cook: {}
Ready in: {}
Recipe: {}
""".format(name, calories, float(rating), rating_count, prep, cook, ready_in, url)

                else:
                    result = 'Sorry, I could not find any results for {}'.format(
                        search_text)

            else:
                result = 'Sorry, your previous search query has failed. Please try searching again.'

        else:
            result = 'I cannot retrieve recipes at this time. Sorry!'

        msg.body(result)
        responded = True

    elif re.search('news*', incoming_msg):  # will search and match new or news or newsssss
        r = requests.get(
            'https://newsapi.org/v2/top-headlines?sources=bbc-news,the-washington-post,the-wall-street-journal,cnn,fox-news,cnbc,abc-news,business-insider-uk,google-news-uk,independent&apiKey=3ff5909978da49b68997fd2a1e21fae8')

        if r.status_code == 200:
            data = r.json()
            articles = data['articles'][:5]
            result = ''

            for article in articles:
                title = article['title']
                url = article['url']
                if 'Z' in article['publishedAt']:
                    published_at = datetime.datetime.strptime(
                        article['publishedAt'][:19], "%Y-%m-%dT%H:%M:%S")
                else:
                    published_at = datetime.datetime.strptime(
                        article['publishedAt'], "%Y-%m-%dT%H:%M:%S%z")
                result += """
*{}*
Read more: {}
_Published at {:02}/{:02}/{:02} {:02}:{:02}:{:02} UTC_
""".format(
                    title,
                    url,
                    published_at.day,
                    published_at.month,
                    published_at.year,
                    published_at.hour,
                    published_at.minute,
                    published_at.second
                )

        else:
            result = 'I cannot fetch news at this time. Sorry!'

        msg.body(result)
        responded = True

    elif incoming_msg.startswith('analyse'):
        # runs task to aggregate data from Apify Covid-19 public actors
        # requests.post('https://api.apify.com/v2/actor-tasks/5MjRnMQJNMQ8TybLD/run-sync?token=qTt3H59g5qoWzesLWXeBKhsXu&ui=1')

        # get the last run dataset items
        # wallet = incoming_msg.replace('analyse', '')
        wallet = incoming_msg.split(" ")
        wallet = wallet[1]

        # api_url = "https://api.bilic.co.uk/rating/address/" + wallet

        # print(str(api_url))
        
        r = requests.get('https://api.bilic.co.uk/rating/address/' + wallet)

        if r.status_code == 200:
            data = r.json()
            print(data)
            
            result= f'{data["bilic_rating"]} ({data["nbr_transaction_count"]})'
        else:
            result = 'I could not retrieve wallet data at this time, sorry.'
        print(result)

        msg.body(result)
        responded = True

    elif re.search('memes*', incoming_msg):
        r = requests.get('https://www.reddit.com/r/memes/top.json?limit=20?t=day',
                         headers={'User-agent': 'your bot 0.1'})

        if r.status_code == 200:
            data = r.json()
            memes = data['data']['children']
            random_meme = random.choice(memes)
            meme_data = random_meme['data']
            title = meme_data['title']
            image = meme_data['url']

            msg.body(title)
            msg.media(image)

        else:
            msg.body('Sorry, I cannot retrieve memes at this time.')

        responded = True

        if not responded:
            msg.body(
                "Sorry, I don't understand. Send 'hello' for a list of commands.")

    if re.search('developer', incoming_msg):
        mess = """
        Guess its who!!😎
        Its your buddy Alex.🥳
        
         More updates are coming soon..
         
         Report any error @ 0711521508
         
         Thank you very much!!💖
        """
        msg.body(mess)
        responded = True

    if not responded:
        msg.body(response1)
    return str(resp)


'''
todo:
ChatGPT Bot
Get Wallet Risk Score
Get Number Risk Score
Send Money to Wallet 
'''


if __name__ == '__main__':
    app.run(debug=True)


