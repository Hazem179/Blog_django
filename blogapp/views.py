from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render,get_object_or_404
from django.contrib.postgres.search import SearchVector,SearchQuery,SearchRank
from .models import Post,Comment
from .forms import EmailPostForm,CommentForm,SearchForm
from django.views.generic import ListView
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
# Create your views here.

# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts' # for query result
#     paginate_by = 3
#     template_name = 'post/list.html'
def post_list(request,tag_slug=None):
    objects = Post.published.all()
    paginator = Paginator(objects,3)
    page = request.GET.get('page')
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag,slug = tag_slug)
        objects = objects.filter(tags__in=[tag])
    try:
            posts = paginator.page(page)
    except PageNotAnInteger:
            # If page is not an integer deliver the first page
            posts = paginator.page(1)
    except EmptyPage:
            # If page is out of range deliver last page of results
            posts = paginator.page(paginator.num_pages)
    return render(request,'post/list.html',{'page':page,'posts':posts,'tag':tag})

def post_detail(request,post,year,month,day):
    post = get_object_or_404(Post,slug = post,publish__year = year,publish__month = month,publish__day = day)
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data = request.POST)
        if comment_form.is_valid():
            # create comment object but don't save it to the database until assigning it to the current post
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

    return render(request,'post/detail.html', {'post':post,
                                               'comments':comments,
                                               'new_comment':new_comment,
                                               'comment_form':comment_form,
                                               'similar_posts':similar_posts,})

def post_share(request,post_id):
    post = get_object_or_404(Post,id = post_id)
    sent = False
    if request.method=='POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'hazemm913@gmail.com.com',
                      [cd['to']])
            sent = True
    # if the request isn't post that's mean the req method is GET
    else:
        form = EmailPostForm()

    return render(request,'post/share.html',{'post':post,
                                             'form':form,
                                             'sent': sent})



def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
    if form.is_valid():
        search_vector = SearchVector('title','body')
        search_query = SearchQuery(query)
        query = form.cleaned_data['query']
        results = Post.published.annotate(
        search=search_vector,
            rank = SearchRank(search_vector,search_query)
            ).filter(search=query).order_by('-rank')

    return render(request,'post/search.html',{'form':form,'query':query,'results':results})