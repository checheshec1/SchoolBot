import re
from collections import defaultdict
import nltk
import string
import unicodedata
from nltk.corpus import wordnet


def Normalize(text):
    text = ''.join([ch for ch in text if ch not in string.punctuation])#Удаление пунктуации/символов
    #word_tokens = nltk.word_tokenize(text.lower())
    word_tokens = nltk.word_tokenize(text)#Токенизация по словам

    #Нормализация слов
    new_words = []
    for word in word_tokens:
        new_word = unicodedata.normalize('NFKC', word)
        new_words.append(new_word)

    #Удаление тегов
    tag_remove = []
    for word in new_words:
        text = re.sub("&lt;/?.*?&gt;", "&lt;&gt;", word)
        tag_remove.append(text)

    #Тегирование части речи и лемматизация
    tag_map = defaultdict(lambda : wordnet.NOUN)
    tag_map['J'] = wordnet.ADJ
    tag_map['V'] = wordnet.VERB
    tag_map['R'] = wordnet.ADV
    lmtzr = nltk.WordNetLemmatizer()
    lemma_list = []
    rmv = [i for i in tag_remove if i]
    for token, tag in nltk.pos_tag(rmv):
        lemma = lmtzr.lemmatize(token, tag_map[tag[0]])
        lemma_list.append(lemma)

    return lemma_list