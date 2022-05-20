from .models import ContentPost



def calculate_news_bar(game=None,group=None):

    if game:
        print('\n\ngame has been set optional parameter used\n\n')
    
    news_all=ContentPost.objects.all().order_by('-headline','-date_posted')

    #this seems like a terrible way to take the first 5 enteries but here we are
    news=[]
    if news_all:
        news+=[news_all.first()]
        news_all=news_all.exclude(id=news_all.first().id)
    if news_all:
        news+=[news_all.first()]
        news_all=news_all.exclude(id=news_all.first().id)
    if news_all:
        news+=[news_all.first()]
        news_all=news_all.exclude(id=news_all.first().id)
    if news_all:
        news+=[news_all.first()]
        news_all=news_all.exclude(id=news_all.first().id)
    if news_all:
        news+=[news_all.first()]
        news_all=news_all.exclude(id=news_all.first().id)
    return news
