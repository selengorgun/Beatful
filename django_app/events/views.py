from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from .models import Event


class EventView(ListView):
    model = Event
    template_name = 'events.html'
    context_object_name = 'events'
    paginate_by = 10
    queryset = Event.objects.all()


class EventInfoView(View):
    def get(self, request, pk):
        event = Event.objects.get(pk=pk)
        return render(request, 'event_information.html', {'event': event})
