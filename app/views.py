from django.shortcuts import render, redirect
import re
from transformers import AutoModelForQuestionAnswering,AutoTokenizer,pipeline
from facebook_scraper import get_posts

from .forms import ScrapeForm

PATH = '../Bert_Arabic-SQuADv2-QA/'
nlp_QA=pipeline('question-answering',model=PATH,tokenizer=PATH)


def nlp_extraction(context):
    item = nlp_QA({
        'question': "ماذا يعرض هذا الاعلان؟",
        'context': context
    })
    location = nlp_QA({
        'question': 'اين مكان؟',
        'context': context
    })
    price = nlp_QA({
        'question': 'كم ثمن؟',
        'context': context
    })
    # phone = nlp_QA({
    #     'question': "رقم الهاتف؟",
    #     'context': context
    # })
    return({
        'item':item["answer"],
        'location':location["answer"],
        'price':price["answer"]
        # 'phone':phone["answer"]
    })
#phone number extraction
def translate_numerals(text):
    ar_num = '٠۰١٢٣٤٥٦٧٨٩'
    en_num = '00123456789'
    table = str.maketrans(ar_num,en_num)
    return text.translate(table)
def phone_extraction(text):
    text = translate_numerals(text)
    phones = []
    for s in text.split():
        s = re.sub(r'[^0-9]', '', s)
        if s[:2] == '01':
            phones.append(s)
    return phones

def cardify(data):
    nlp_card = nlp_extraction(data['text'])
    phones = phone_extraction(data['text'])
    if nlp_card['price'] in phones or nlp_card['price'].isdigit() == False:
        nlp_card['price'] ='N/A'
    return(
        {
            'post_id': data['post_id'],
            'text': data['text'],
            'item': nlp_card["item"],
            'location': nlp_card["location"],
            'price': nlp_card["price"],
            'phones': phones,
            'post_url': data['post_url'],
            'time': data['time']
        }
    )
# Create your views here.
cards = [
    # {
    #     'post_id': 1,
    #     'text': "lorem ipsum",
    #     'item': "lorem ipsum",
    #     'location': "lorem ipsum",
    #     'price': "lorem ipsum",
    #     'phones': None,
    #     'post_url': "lorem ipsum",
    #     'time': "lorem ipsum"
    # },
    # {
    #     'post_id': 2,
    #     'text': "lorem ipsum",
    #     'item': "lorem ipsum",
    #     'location': "lorem ipsum",
    #     'price': "lorem ipsum",
    #     'phones': None,
    #     'post_url': "lorem ipsum",
    #     'time': "lorem ipsum"
    # }
]
def cards_view(request):
    return render(request, "cards.html", context={"cards": cards})

async def scrape(request):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = ScrapeForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            group_id = request.POST.get('group_id')
            print(group_id)
            # cards = []
            for post in get_posts(group=group_id,pages=1):
                cards.append(cardify(post))
            return render(request, "scrape.html", context={"form":form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ScrapeForm()
    return render(request, "scrape.html", {"form": form})


def command(request, id, cmd):
    for card in cards:
        if id == card["post_id"]:
            if cmd == "delete":
                cards.remove(card)
    return redirect("/")