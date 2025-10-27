from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import BlogPost

def post_list(request):
    posts = BlogPost.objects.filter(is_published=True).order_by('-published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.POST.get('author')
        is_published = request.POST.get('is_published') == 'on'
        
        if title and content and author:
            post = BlogPost.objects.create(
                title=title,
                content=content,
                author=author,
                is_published=is_published
            )
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', pk=post.pk)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'blog/post_form.html')

def post_update(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.author = request.POST.get('author')
        post.is_published = request.POST.get('is_published') == 'on'
        post.save()
        
        messages.success(request, 'Post updated successfully!')
        return redirect('post_detail', pk=post.pk)
    
    return render(request, 'blog/post_form.html', {'post': post})

def post_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('post_list')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

