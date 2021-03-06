from django.shortcuts import render


from django.http import HttpResponse

#def index(request):
   # return HttpResponse('Hello, World!')

from catalog.models import Book, Author, BookInstance, Genre

def index(request):
    
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    
      
    num_authors = Author.objects.count()
    
    # example of session set.......

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    #del request.session['num_visits']
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }
    
    # Render the HTML template index.html with the data in the context variable.
    return render(request, 'index.html', context=context)

from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 1

class BookDetailView(generic.DetailView):
    model = Book    


from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')



from django.contrib.auth.mixins import PermissionRequiredMixin


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')



import datetime

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    
    book_instance = get_object_or_404(BookInstance, pk=pk)

   
    if request.method == 'POST':

       
        form = RenewBookForm(request.POST)

        
        if form.is_valid():
           
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            
            return HttpResponseRedirect(reverse('all-borrowed') )

   
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)





from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2200'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
