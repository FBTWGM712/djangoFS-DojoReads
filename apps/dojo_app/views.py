from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import bcrypt

# Create your views here.
def index(request):
    if 'id' in request.session.keys():
        return redirect ('/books')
    return render(request, "index.html")

def register(request):
    if request.method == 'POST':
        errors = User.objects.reg_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        else:
            password = request.POST['password']
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()  
            print(pw_hash)   

            new_user = User.objects.create(
                name=request.POST['name'], 
                alias=request.POST['alias'], 
                email=request.POST['email'], 
                password=pw_hash)
            print(new_user)
            request.session['user_id'] = new_user.id
            request.session['alias'] = new_user.alias
            request.session['user_name'] = f"{new_user.name} {new_user.alias}"
            request.session['status'] = "registered"
            request.session['isloggedin'] = True

        return redirect("/books") # nunca renderizar en una publicación, ¡siempre redirigir!
    return redirect("/")

def login(request):
    if request.method == 'POST':
        errors = User.objects.log_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        else:
            user = User.objects.filter(alias=request.POST['alias'])
            if user:
                logged_user = user[0] #solo hay un usuario con ese alias, por lo que se usa [0]
                if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
                    request.session['user_id'] = logged_user.id
                    request.session['alias'] = logged_user.alias
                    request.session['user_name'] = f"{logged_user.name}"
                    request.session['status'] = "Logged in"
                    request.session['isloggedin'] = True
            
                    return redirect('/books')
                else: 
                    messages.error(request, "password invalid")
        return redirect("/")

def logout(request):
    request.session.clear()
    request.session['isloggedin'] = False
    return redirect('/')
# **************************************

#homepage / view all user_books
def books(request):
    if not request.session['isloggedin']:
        return redirect('/')
    else:
        user_alias = request.session['alias']
        user = User.objects.get(alias=user_alias)
        latest_reviews = Review.objects.order_by("-created_at")[:3]
        all_books = Book.objects.order_by("title")

        context = {
                    "first": user.name,
                    "email": user.email,
                    "reviews_submitted": user.reviews_submitted,
                    "latest_reviews": latest_reviews,
                    "all_books": all_books
                    }
        return render(request, 'books.html', context)

def add(request):
    if not request.session['isloggedin']:
        return redirect('/')
    else:
        author_list = Book.objects.values('author').distinct()
        context = {
                    "authors" : author_list
        }
        return render(request, 'add.html', context)

#add book to db
def add_book_to_db(request):
    if not request.session['isloggedin']:
        return redirect('/')
    else:
        errors = Book.objects.book_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
            return redirect('/books/add')

        else:
            if request.POST.get("author_list") != "none":
                select_author_from = request.POST.get('author_list')
            else:
                select_author_from = request.POST["author_name"]

            title=request.POST["title"]
            author=select_author_from
            review = request.POST['review']
            rating= request.POST.get('rating')
            this_user = User.objects.get(alias=request.session['alias'])

            this_book = Book.objects.create(
            title = title,
            author = author,
            submitted_by = this_user
            )
            Review.objects.create(review=review, rating=rating, reviewer=this_user, book=this_book)
            return redirect('/books/'+str(this_book.id))


#view book
def view_book(request, id):
    if not request.session['isloggedin']:
        return redirect('/')
    else:
        this_book = Book.objects.get(id=id)
        current_user = User.objects.get(alias=request.session["alias"])
        context = {
            "book" : this_book,
            "reviews": Review.objects.filter(book=this_book).order_by("-created_at"),
            "current_user": current_user,
        }

        return render(request, 'view_book.html', context)

#add a Review

def add_review(request, book_id):
    if not request.session['isloggedin']:
        return redirect('/')
    else:
        errors = Book.objects.review_validator(request.POST)
        print("gets to add review") 

        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
                return redirect('/books/' + str(book_id))
                print("VALIDATOR ERRORS") 
        else:
            review = request.POST["review"]
            rating = request.POST.get("rating")
            reviewer = User.objects.get(alias=request.session["alias"])
            this_book = Book.objects.get(id=book_id)
            print("SUBMITTING TO DB") 

            Review.objects.create(review=review, rating=rating, book=this_book, reviewer=reviewer)

            return redirect('/books/' + str(book_id))


#confirmation page for deleting review
def confirm_delete_review(request, id):
    if not request.session['isloggedin']:
        return redirect('/')
    else:
        review = Review.objects.get(id=id)
        context = {
                "review": review,
                    }

        return render(request, 'confirm_delete.html', context)
#removing review from the db
def delete_review(request, id):
    if not request.session['isloggedin']:
        return redirect('/')
    else:
        review = Review.objects.get(id=id)
        book_id = review.book.id

        review.delete()

        return redirect('/books/' +str(book_id))

#view a user
def user(request, id):
    if not request.session['isloggedin']:
        return redirect('/')
    else:
        user = User.objects.get(id=id)
        reviews = Review.objects.filter(reviewer=id).order_by("-created_at")
        total_reviews = Review.objects.filter(reviewer=id).count()
        context = {
                "user": user,
                "reviews": reviews,
                "total_reviews": total_reviews,
                    }

        return render(request, 'user.html', context)

