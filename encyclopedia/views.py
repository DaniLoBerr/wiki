from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from markdown2 import markdown
from random import choice

from . import util


class NewEntryForm(forms.Form):
    """Form for creating a new entry with a title and content. Extends
    forms.Form.
    
    :attr title: The title of the entry, displayed as a single-line text
        input with a "Title" label.
    :type title: CharField
    :attr content: The content of the entry, displayed as a multi-line
        textarea with a "Content" label.
    :type content: CharField
    """
    title = forms.CharField(label="Title")
    content = forms.CharField(
        label="Content",
        widget=forms.Textarea()
    )


class NewEditForm(forms.Form):
    """Form for editing the content of an existing entry. Extends
    forms.Form.
    
    :attr content: A multi-line text area labeled "Edit content" for
        modifying the entry's text.
    :type content: CharField
    """
    content = forms.CharField(
        label="Edit content",
        widget=forms.Textarea(),
    )


def index(request):
    """Render the homepage displaying a list of all encyclopedia entries.

    This view fetches the list of all entries and renders the index
    template with the entries passed in the context.
    
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: The HttpResponse with rendered index page.
    :rtype: HttpResponse
    """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    """Render a specific encyclopedia entry by title.

    Searches for an entry matching the given title against the fetched
    list of all entries case-insensitively.
    If found, it retrieves and renders the entry content converted to
    HTML. Otherwise, it renders a error page.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param title: The title of the encyclopedia entry to display.
    :type title: str
    :return: The HTTP response with rendered entry page or error page.
    :rtype: HttpResponse
    """
    for ent in util.list_entries():
        if ent.casefold() == title.casefold():
            case_title = ent
            break

    content = util.get_entry(case_title)

    if content is None:
        return render(request, "encyclopedia/error.html", {
            "content": "The requested page was not found."
        })

    return render(request, "encyclopedia/entry.html", {
        "title": case_title,
        "content": markdown(content),
    })


def search(request):
    """Render a specific encyclopedia entry by query or show search
    results.

    If the query exactly matches an entry title (case-insensitively),
    redirect to that entry's page. Otherwise, render a search results
    page listing all encyclopedia entries containing the query as a
    case-insensitively substring.  that have
    If no entries match, render a search results page with a not entries
    found message.
    
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: The HTTP response with rendered entry page or results page.
    :rtype: HttpResponse
    """
    entries = util.list_entries()
    query = request.GET.get("q").strip()
    results = []

    for ent in entries:
        if query.lower() == ent.lower():
            return HttpResponseRedirect(reverse('encyclopedia:entry', args=[ent]))
        elif query.lower() in ent.lower():
            results.append(ent)

    return render(request, "encyclopedia/search.html", {"results": results})


def new(request):
    """Handle creation of a new encyclopedia entry.

    On GET, renders a form for creating a new entry.
    On POST, validates the form, checks for duplicates, saves the entry,
    and redirects to the entry page. If a duplicate exists, renders an
    error page.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: HTTP response rendering the form, error page, or redirect
        to the new entry page or results page.
    :rtype: HttpResponse
    """
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            entries = util.list_entries()

            for ent in entries:
                if ent.lower() == title.lower():
                    return render(request, "encyclopedia/error.html", {
                        "content": f"{title} entry already exists."
                    })
            
            util.save_entry(title, content)

            return HttpResponseRedirect(
                reverse('encyclopedia:entry', args=[title])
            )

    return render(request, "encyclopedia/new.html", {
        "form": NewEntryForm(),
    })


def edit(request, title):
    """Edit an existing encyclopedia entry.

    On GET, displays a form pre-populated with the entry's content.
    On POST, validates the submitted form, updates the entry, and
    redirects to the entry page.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param title: The title of the encyclopedia entry to edit.
    :type title: str
    :return: HTTP response rendering the edit form or redirect
        to the updated entry page.
    :rtype: HttpResponse
    """
    if request.method == "POST":
        form = NewEditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(
                reverse('encyclopedia:entry', args=[title])
            )

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": NewEditForm(initial={"content": util.get_entry(title)}),
    })


def random(request):
    """Redirect to a random encyclopedia entry.

    Picks a random entry from the list of all entries and redirects the
    user to its page. If there are no entries, displays an error page.
    
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: HTTP response rendering a random entry or an error page.
    :rtype: HttpResponse
    """
    entries = util.list_entries()
    if not entries:
        return render(request, "encyclopedia/error.html", {
            "content": "No entries found."
        })
    return HttpResponseRedirect(
        reverse('encyclopedia:entry', args=[choice(entries)])
    )