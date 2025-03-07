from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import requests
n=0
if n==0:
    tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
    model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
    n+=1
def sentiment_score(message):
    tokens = tokenizer.encode(message, return_tensors='pt')
    result = model(tokens)
    return int(torch.argmax(result.logits))+1
