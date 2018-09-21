# coding=utf-8

# Progetto: Pushetta API 
# Indici per il motore di ricerca

from haystack import indexes

from core.models import Channel

'''
class ChannelIndex(indexes.ModelSearchIndex, indexes.Indexable):
    class Meta:
        model = Channel

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        # filter(kind!=PRIVATE).
        return self.get_model().objects.filter(hidden=False)
'''


class ChannelIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    
    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description')
    image = indexes.CharField(model_attr='image')
    hidden = indexes.BooleanField(model_attr='hidden')
    kind = indexes.IntegerField(model_attr='kind')
    subscriptions = indexes.IntegerField(model_attr='subscriptions')

    def get_model(self):
        return Channel


    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        # filter(kind!=PRIVATE).
        return self.get_model().objects.filter(hidden='false')
