from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

# validating email addresses
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from django.contrib import messages

from core.forms import RegistrationForm, SubmissionForm
from core.models import Image, Vote, Category, VoteCount

from core.tasks import scrapers

from django.utils import simplejson
def json_response(obj):
    """
    Helper method to turn a python object into json format and return an HttpResponse object.
    """
    return HttpResponse(simplejson.dumps(obj), mimetype="application/x-javascript")

#
# Views that deal with user authentication
#
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            
            user = User.objects.create_user(email, #email is username
                                            email, #email
                                            password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return authenticate(request, email, password)
    else:
        # setup the redirect url if user attempted to access a page
        # that required login
        if 'next' in request.GET:
            request.session['next'] = request.GET['next']
        form = RegistrationForm()
    
    return render_to_response("login.html", {
            'form': form,
        },
        context_instance = RequestContext(request)
    )

def authenticate(request, email, password):
    user = auth.authenticate(username=email, password=password)
    if user is not None:
        if not user.is_active:
            auth.logout(request)
            return redirect('/?msg=notactive') #TODO

        auth.login(request, user)
        
        if 'next' in request.session:
            next = request.session['next']
            del request.session['next']
            return redirect(next)
        
        return redirect('/')
    else:
        form = RegistrationForm()
        return render_to_response("login.html", {
                'login_error': True, # indicates username / pword did not match
                'form': form,
            },
            context_instance = RequestContext(request)
        )

@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')

@csrf_protect
def login(request):
    if request.method == "POST":
        return authenticate(request, request.POST['email'], request.POST['password'])
    return redirect('/register')
    
def manual(request):
    scrapers.delay()
    return HttpResponse("Manually updating images...")

#
# Onsite interactions
#

def image(request, image_id):
    im = get_object_or_404(Image, pk=int(image_id))
    return render_to_response("image.html", {
            'im': im
        },
        context_instance = RequestContext(request)
    )

def list(request, category):
    category = get_object_or_404(Category, pk=int(category))
   
    images = category.image_set.all()
    
    # TODO fold this ordering into the above query
    images = sorted(images, key=lambda im: VoteCount.get_vote_count(image_id=im.pk, cat_id=category.pk), reverse=True)
    
    categories = Category.objects.all()
    
    return render_to_response("index.html", {
            'images': images,
            'categories': categories,
            'category': category
        },
        context_instance = RequestContext(request)
    )

@login_required
def submit(request):
    if request.method == "POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            caption = form.cleaned_data['caption']
            url = form.cleaned_data['image_url']
            categories = form.cleaned_data['categories']
            
            im = Image(caption=caption, 
                       url=url,
                       user=request.user)
            im.save() # need to save before adding many to many relationships
            im.apply_categories(categories)
            
            messages.success(request, 'Image submitted successfully!')
            return redirect('/submit')
    else:
        form = SubmissionForm()
    
    return render_to_response("submit.html", {
            'form': form,
        },
        context_instance = RequestContext(request)
    )

@csrf_protect
def index(request):
    images = Image.objects.order_by("-created")
    categories = Category.objects.all()
    return render_to_response("index.html", {
            'images': images,
            'categories': categories
        },
        context_instance = RequestContext(request)
    )

#
# Ajax views
#
@csrf_protect  
def vote(request):
    if not request.user.is_authenticated():
        return json_response({
            "status": "fail",
            "why": "login"
        })
    votes = Vote.submit_vote(request)
    return json_response({
        "status": "ok",
        "votes": votes
    })