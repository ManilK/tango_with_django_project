import os
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm


def encode_url(str):
    return str.replace(' ', '_')

def decode_url(str):
    return str.replace('_', ' ')


def index(request):
    # Request the context of the request.
    # The context contains information such as the clients machine details, for example
    context = RequestContext(request)
    
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    category_list = Category.objects.order_by('-likes')[:5]
        
    # Construct a dictionary to pass pages to template engine
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {'categories': category_list, 'pages': page_list}
    # The following two lines are new
    # We loop through each category returned, and create a URL attribute,
    # This attribute stores an encoded URL (e.g. space replace with underscores)
    for category in category_list:
        category.url = encode_url(category.name)
#    for category in category_list:
#        category.url = category.name.replace(' ','_')
    
    #Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier
    # Note that the first parameter is the template we wish to use
    return render_to_response('rango/index.html', context_dict, context)
    
    #return HttpResponse("Rango says hello world!  <a href='/rango/about'>About</a>")

def about(request):
    context = RequestContext(request)
    return render_to_response('rango/about.html',context)

def category(request, category_name_url):
    # Request our context from the request passed to us.
    context = RequestContext(request)

    # Change underscores in the category name to spaces.
    # URLs don't handle spaces well, so we encode them as underscores.
    # We can then simply replace the underscores with spaces again to get the name.
    category_name = category_name_url.replace('_', ' ')

    # Create a context dictionary which we can pass to the template rendering engine.
    # We start by containing the name of the category passed by the user.
    context_dict = {'category_name': category_name, 'category_name_url': category_name_url}

    try:
        # Can we find a category with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(name__iexact=category_name)

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client.
    return render_to_response('rango/category.html', context_dict, context)

def add_category(request):
    # Get the context from the request.
    context = RequestContext(request)
    
    # A HTTP POST?
    if (request.method == 'POST'):
        form = CategoryForm(request.POST)
        
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)
            
            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            #print form.errors
            pass
    else:
        # If the request was not a POST, display the form
        form = CategoryForm()
        
        # Bad form (or form details), no form supplied...
        # Render the form with error messages (if any). 
    return render_to_response('rango/add_category.html', {'form': form}, context)  

def add_page(request, category_name_url):
    context = RequestContext(request)
    
    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            # This time we cannot commit straight away
            # Not all fields are automatically populated!
            page = form.save(commit=True)
            
            # Retrieve the associated Category object so we can add it
            # Wrap the code in a try block - check if the catgory actually exists
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                # If we get here, the category does not exist
                # GO back and render the add category form as a way of saying the category does not exist
                return render_to_response('rango/add_category.html', {}, context)
            
            # Also, create a default value for the number of views
            page.views = 0
            
            # With this, we can then save our new model instance
            page.save()
            
            # Now that the page is saved, display the category instead
            return category(request, category_name)
        else:
            print form.errors
    else:
        form = PageForm()
        
    return render_to_response( 'rango/add_page.html',
                               {'category_name_url': category_name_url,
                                'category_name': category_name, 'form': form},
                                context)
    
def register(request):
    # Like before, get the request's context
    context = RequestContext(request)
    
    registered = False
    
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            user.set_password(user.password)
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            
            registered = True
            
        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render_to_response(
                'rango/register.html',
                {'user_form': user_form,
                 'profile_form': profile_form,
                 'registered': registered},
                context)
        
def user_login(request):
    context = RequestContext(request)
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your Rango account is disabled")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
    
    else:
        return render_to_response('rango/login.html', {}, context)
    
@login_required    
def user_logout(request):
    logout(request)
    
    return HttpResponseRedirect('/rango/')

@login_required
def restricted(request):
    return HttpResponse("since you're logged in, you can see this test!")

