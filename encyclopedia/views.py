from django.shortcuts import render

from . import util


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
    If found, it retrieves and renders the entry content. Otherwise, it
    renders a error page.

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
        return render(request, "encyclopedia/error.html")

    return render(request, "encyclopedia/entry.html", {
        "title": case_title,
        "content": content,
    })