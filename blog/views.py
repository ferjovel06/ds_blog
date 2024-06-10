from django.contrib.postgres.search import SearchQuery, TrigramSimilarity
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count, Q
from .models import Post
from django.contrib.postgres.search import SearchVector
from .forms import EmailPostForm, CommentForm, SearchForm


# Create your views here.
def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    all_tags = Tag.objects.all()
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('translations__title', weight='A') + \
                            SearchVector('translations__body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                similarity=TrigramSimilarity('translations__title', query),
            ).filter(Q(similarity__gt=0.1)).order_by('-similarity')

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)  # 3 posts en cada página
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, devuelve la primera página
        posts = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, devuelve la última página de resultados
        posts = paginator.page(paginator.num_pages)
    context = {
        'page': page,
        'posts': posts,
        'tag': tag,
        'all_tags': all_tags,
        'form': form,
        'query': query,
        'results': results
    }
    return render(request, 'blog/list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             translations__slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    all_tags = Tag.objects.all()
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('translations__title', weight='A') + \
                            SearchVector('translations__body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                similarity=TrigramSimilarity('translations__title', query),
            ).filter(Q(similarity__gt=0.1)).order_by('-similarity')

    # Lista de body activos to este post
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # Un comentario fue publicado
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Crear objeto Comments pero no guardarlo en la base de datos
            new_comment = comment_form.save(commit=False)
            # Asignar el post actual al comentario
            new_comment.post = post
            # Guardar el comentario en la base de datos
            new_comment.save()
    else:
        comment_form = CommentForm()

    # Lista de posts similares
    post_tags_ids = post.tags.values_list('id', flat=True)
    related_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    related_posts = related_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    context = {'post': post,
               'comments': comments,
               'new_comment': new_comment,
               'comment_form': comment_form,
               'related_posts': related_posts,
               'form': form,
               'query': query,
               'results': results}
    return render(request,
                  'blog/detail.html',
                  context)


def post_share(request, post_id):
    # Recuperamos la publicación por id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Formulario sent
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Formulario validado correctamente
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            asunto = f"{cd['name']} te recomienda leer " \
                     f"{post.title}"
            mensaje = f"Lee {post.title} en {post_url}\n\n" \
                      f"Comentario de {cd['name']}: {cd['body']}"
            send_mail(asunto, mensaje, 'contactoclinicaemocionalmente@gmail.com',
                      [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/share.html', {'post': post,
                                               'form': form,
                                               'sent': sent})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('translations__title', weight='A') + \
                            SearchVector('translations__body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                similarity=TrigramSimilarity('translations__title', query),
            ).filter(Q(similarity__gt=0.1)).order_by('-similarity')

    return render(request,
                  'blog/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})
