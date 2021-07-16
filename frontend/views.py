import re
from django.shortcuts import render, redirect
from django.utils.timezone import datetime
from django.http import HttpResponse
from django.views.generic import ListView
from frontend.forms import LogMessageForm
from frontend.models import LogMessage
from frontend.internal import MyApplication
from frontend.external import HelloWorldPrinter, AlohaWorldPrinter

class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = LogMessage

    def get_context_data(self, **kwargs):
        return super(HomeListView, self).get_context_data(**kwargs)

def about(request):
    return render(request, "frontend/about.html")

def contact(request):
    return render(request, "frontend/contact.html")

def log_message(request):
    form = LogMessageForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            message = form.save(commit=False)
            message.log_date = datetime.now()
            message.save()
            return redirect("home")
    else:
        return render(request, "frontend/log_message.html", {"form": form})

def plugins(request):
    app = MyApplication(plugins=[HelloWorldPrinter()])
    app.run()

    app = MyApplication(plugins=[AlohaWorldPrinter()])
    app.run()

    app = MyApplication(plugins=[HelloWorldPrinter(), AlohaWorldPrinter()])
    app.run()

    return HttpResponse()