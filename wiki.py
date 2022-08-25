import wikipedia as wk

def wiki_data(request):
    try:
        wk.set_lang('ru')
        wiki = wk.summary(request, sentences = 5)
        return wiki
    except Exception as e:
        return 'Данные не найдены. Повторите попытку позднее.'