import json
from django.http import HttpResponse, JsonResponse
import random
def quotes(request):
    with open('quotes.json', 'r') as f:
        quotes_data = json.load(f)
    
    random_quote = random.choice(quotes_data)
    # print(random_quote)
    return {'random_quote': random_quote}