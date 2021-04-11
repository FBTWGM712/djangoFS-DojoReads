from __future__ import unicode_literals

from django.db import models

import re, bcrypt

# Create your models here.

class UserManager(models.Manager):
    def reg_validator(self, postData):
        email_regex =  re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        errors = {}
        # print(postData)
        if User.objects.filter(email = postData['email']):
            errors['email_exists'] = "An account is already associated with that email"
        if (len(postData['name']) < 1) or (len(postData['alias']) < 1) or (len(postData['email']) < 1):
            errors["blank"] = "All fields are required and must not be blank!"
        if len(postData['name']) < 2:
            errors['name'] = "needs to be longer than 2 characters"
        if len(postData['alias']) < 2:
            errors['alias'] = "needs to be longer than 2 characters"
        if not email_regex.match(postData['email']):
            errors['email']="Email must be a valid format"
        if len(postData['password'])<8:
            errors['password']= "Password must be at least 8 character"
        if postData['password'] != postData['confirm']:
            errors['confirm']= "Password and Confirm must match"
        
        return errors
    def log_validator(self, postData):
        user = User.objects.filter(alias= postData['alias'])
        errors = {}
        if not user:
            errors['alias'] = "Insert a valid alias"
        return errors

class BookManager(models.Manager):
    def book_validator(self, postData):
        errors = {}
        title = postData["title"]
        review = postData["review"]
        rating = postData.get("rating")
        try:
            author_check_unique = Book.objects.get(author=postData["author_name"])
        except Book.DoesNotExist:
            author_check_unique = True

        if len(title) == 0:
            errors["title"] = "Please enter a title."
            print("title error") 
        if len(review) == 0:
            errors["review"] = "Please enter your review"
            print("review error") 

        if postData.get("author_list") == 'none' and len(postData["author_name"])  == 0:
            errors["author"] = "Please enter an author's name or select from list."
            print("author error") 
        if author_check_unique != True:
            errors["author"] = "Author already exists, please select from list."
            print("duplicate author") 
        if postData.get('rating') == "none":
            errors["rating"] = "Please select a rating."
        return errors

    def review_validator(self, postData):
        errors={}
        review = postData["review"]
        rating = postData.get("rating")

        if len(review) == 0:
            errors["review"] = "Please enter your review"
            print("ERRORS review") 
        if rating == "none":
            errors["rating"] = "Please select a rating."
            print("ERRORS rating") 
        return errors

class User(models.Model):
    name = models.CharField(max_length=200)
    alias = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects =UserManager()

    def __repr__(self):
        return "<User object: {} {}, {}>".format(
            self.name, self.alias, self.email)

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, null=True)
    submitted_by = models.ForeignKey(User, related_name="books_submitted", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "ID: " + str(self.id) + ", Title: " + self.title + ", Author: " + self.author +  ", Submitted By: " + str(self.submitted_by) + ", Date Added: "\
        + str(self.created_at) + str(self.reviews)

    objects = BookManager()


class Review(models.Model):
    review = models.TextField()
    rating = models.CharField(max_length=1)
    book = models.ForeignKey(Book, related_name="reviews", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, related_name="reviews_submitted", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "Book: " + str(self.book) + ", Reviewer: " + str(self.reviewer) +  ", Rating: " + str(self.rating) + ", Date Added: "\
        + str(self.created_at) + ", Review: " + self.review

    objects = BookManager()