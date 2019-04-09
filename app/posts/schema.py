import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q

from .models import Post, Like
from users.schema import UserType

class PostType(DjangoObjectType):
    class Meta:
        model = Post

class LikeType(DjangoObjectType):
    class Meta:
        model = Like

class Query(graphene.ObjectType):
    posts = graphene.List(PostType, search=graphene.String())
    likes = graphene.List(LikeType)

    def resolve_posts(self, info, search=None):
        # title__startswith, exact, iexact, gt
        if search:
            filter = (
                Q(title__icontains=search | description__icontains=search)
            )
            return Post.objects.filter
        return Post.objects.all()

    def resolve_likes(self, info):
        return Likes.objects.all()

class CreatePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()

    def mutate(self, info, title, description, url):
        user = info.context.user or None

        if user.is_anonymous:
            raise GraphQLError('login to create post')

        post = Post(title=title, description=description, url=url, posted_by=user)
        post.save()
        return CreatePost(post=post)

class UpdatePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        post_id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()

    def mutate(self, info, post_id, title, url, description):
        user = info.context.user
        post = Post.objects.get(id=post_id)

        if post.posted_by != user:
            raise GraphQLError('Not permitted to update this post.')

        post.title = title
        post.description = description
        post.url = url

        post.save()

        return UpdatePost(post=post)
    
class DeletePost(graphene.Mutation):
    post_id = graphene.Int()

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        post = Post.objects.get(id=post_id)

        if post.posted_by != user:
            raise GraphQLError('Not permitted to delete post')

        post.delete()

        return DeletePost(post_id=post_id)

class CreateLike(graphene.Mutation):
    user = graphene.Field(UserType)
    post = graphene.Field(PostType)

    class Arguments:
        post_id = graphene.Int(required=True)
    
    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('login to do it')
        
        post = Post.objects.get(id=post_id)
        if not post:
            raise GraphQLError('cannot frimd post id')

        Like.objects.create(
            user=user,
            post=post
        )

        return CreateLike(user=user, post=post)

class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    create_post = CreatePost.Field()
 