from rest_framework.views import APIView
from rest_framework import permissions, status, generics
from rest_framework.response import Response

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User

from .models import Quote, Show, Role
from .serializers import (
	QuoteSerializer, AdminQuoteSerializer,
	AdminAddUserSerializer, ShowSerializer, RoleSerializer)
from statistic.utils import get_client_ip, add_or_create_visit


class MainPage(APIView):
	"""Show the main frontend page"""
	permission_classes = (permissions.AllowAny, )

	def get(self, request, format=None):
		return render(request, 'index.html')


class UserQuoteView(APIView):
	"""Show a random quote to the user"""
	permission_classes = (permissions.AllowAny, )

	def get(self, request, format=None):
		ip = get_client_ip(request)
		add_or_create_visit(ip)
		if "censored" in request.query_params:

			all_quotes_random = Quote.objects.filter(
				contain_adult_lang=False).order_by("?")
		else:
			all_quotes_random = Quote.objects.all().order_by("?")

		if all_quotes_random.count() == 0:
			return Response(
				status=status.HTTP_200_OK,
				data={
					"detail": "No quote available please try again later.",
					"status": "no_quote"
				}
			)
		serializer = QuoteSerializer(instance=all_quotes_random.first())
		return Response(status=status.HTTP_200_OK, data=serializer.data)


class SpecificShowQuotes(APIView):
	"""Show a random quote from the given slug show (shows slug are listed in
	the mainpage)"""
	permission_classes = (permissions.AllowAny, )

	def get(self, request, slug, format=None):
		ip = get_client_ip(request)
		add_or_create_visit(ip)
		requested_show = get_object_or_404(Show, slug=slug)
		if not requested_show.show.all().exists():
			return Response(
				status=status.HTTP_204_NO_CONTENT,
				data={
					"detail": "no quote for this show yet.",
					"status": "no_quote_for_show"
				}
			)

		quote = requested_show.show.all().order_by("?").first()

		serializer = QuoteSerializer(instance=quote)
		return Response(status=status.HTTP_200_OK, data=serializer.data)


class AdminQuoteView(generics.ListCreateAPIView):
	"""GET show all quotes at once (admin only)
	POST add new quote (included quote, show, role) (admins only),
	show and role should send as string (not object) which is the name of them,
	object will create on the server side"""

	queryset = Quote.objects.all()
	permission_classes = (permissions.IsAdminUser, )
	serializer_class = AdminQuoteSerializer


class AdminEditAndDeleteQuoteView(APIView):
	"""edit quotes get field 'quote', 'role', 'show'
	should include quote key in the url.
	only can change show and role to an existed show and role object."""

	permission_classes = (permissions.IsAdminUser, )

	def put(self, request, key, format=None):
		if "quote" not in request.data and "show" not in request.data and "role" not\
			in request.data and "contain_adult_lang" not in request.data:
			return Response(
				status=status.HTTP_400_BAD_REQUEST,
				data={"detail": "no new data provided"}
			)

		quote = get_object_or_404(Quote, key=key)
		if "show" in request.data:
			show = get_object_or_404(Show, name=request.data["show"].title())
			quote.show = show
		if "role" in request.data:
			role = get_object_or_404(Role, name=request.data["role"].title())
			quote.role = role
		if "quote" in request.data:
			quote.quote = request.data["quote"]
		if "contain_adult_lang" in request.data:
			quote.contain_adult_lang = request.data["contain_adult_lang"]
		quote.save()
		return Response(status=status.HTTP_200_OK, data={"detail": "updated"})

	def delete(self, request, key, format=None):
		quote = get_object_or_404(Quote, key=key)
		quote.delete()
		return Response(status=status.HTTP_200_OK, data={"detail": "deleted"})


class AdminEditShowView(APIView):
	"""Edit show get field 'name' should include show slug in url"""
	permission_classes = (permissions.IsAdminUser, )

	def put(self, request, slug, format=None):
		if "name" not in request.data:
			return Response(
				status=status.HTTP_400_BAD_REQUEST,
				data={
					"detail": "no new data provided.",
					"name": "this field is required."
				}
			)

		show = get_object_or_404(Show, slug=slug)
		show.name = request.data["name"]
		show.save()
		return Response(status=status.HTTP_200_OK, data={"detail": "show updated"})


class AllShowsView(generics.ListAPIView):
	"""List all shows"""
	permission_classes = (permissions.AllowAny, )
	serializer_class = ShowSerializer
	queryset = Show.objects.all()


class AdminEditRoleView(APIView):
	"""Edit role get field 'name' should include role slug in url."""
	permission_classes = (permissions.IsAdminUser, )

	def put(self, request, slug, format=None):
		if "name" not in request.data:
			return Response(
				status=status.HTTP_400_BAD_REQUEST,
				data={
					"detail": "no new data provided.",
					"name": "this field is required."
				}
			)

		role = get_object_or_404(Role, slug=slug)
		role.name = request.data["name"]
		role.save()
		return Response(status=status.HTTP_200_OK, data={"detail": "role updated."})


class AdminAllRolesView(generics.ListAPIView):
	"""Show all roles to admin user."""
	permission_classes = (permissions.IsAdminUser, )
	serializer_class = RoleSerializer
	queryset = Role.objects.all()


class AdminUserView(generics.ListCreateAPIView):
	"""GET return all users (admin only).
	POST add new user (admin only) [username, first_name, last_name, email,
	password1, password2](only main superuser can make user).
	"""

	queryset = User.objects.all()
	permission_classes = (permissions.IsAdminUser, )
	serializer_class = AdminAddUserSerializer


class AdminEditUserView(APIView):
	"""Edit user credentials (every user can edit it selves profile.
	also main superuser can edit every users profile.).
	it should include at least one of : [first_name, last_name, username, email,
	(together [password1,password2]), (only main superuser can modify this
	[is_superuser, is_active, is_staff]) ].
	"""

	permission_classes = (permissions.IsAuthenticated, )

	def put(self, request, pk, format=None):
		user = request.user
		main_superuser_username = User.objects.filter(
			is_superuser=True,
			is_staff=True,
			is_active=True
		).first().username
		if user != User.objects.get(pk=pk) and not user.is_superuser\
			and user.username != main_superuser_username:
			return Response(
				status=status.HTTP_401_UNAUTHORIZED,
				data={"detail": "you don't have permission for this user"})

		instance = get_object_or_404(User, pk=pk)

		if "first_name" in request.data:
			instance.first_name = request.data['first_name']
		if "last_name" in request.data:
			instance.last_name = request.data['last_name']
		if "username" in request.data:
			if User.objects.filter(username=request.data['username']).exists():
				return Response(
					status=status.HTTP_400_BAD_REQUEST,
					data={"detail": "username already exist"})

			instance.username = request.data['username']
		if "email" in request.data:
			try:
				validate_email(request.data["email"])
			except ValidationError as eex:
				return Response(
					status=status.HTTP_400_BAD_REQUEST, data={"detail": {"email": eex}})

			instance.email = request.data['email']

		if "password1" in request.data:
			if "password2" not in request.data:
				return Response(
					status=status.HTTP_400_BAD_REQUEST,
					data={"detail": "password2 field not provided"})

			if request.data['password1'] != request.data["password2"]:
				return Response(
					status=status.HTTP_400_BAD_REQUEST,
					data={"detail": "password fields don't match"})

			try:
				validate_password(request.data['password1'], user)
				instance.set_password(request.data['password1'])
			except ValidationError as ex:
				return Response(
					status=status.HTTP_400_BAD_REQUEST, data={"detail": {"password": ex}})

		if "is_superuser" in request.data or "is_active" in request.data\
			or "is_staff" in request.data:
			if user.username != main_superuser_username:
				return Response(
					status=status.HTTP_401_UNAUTHORIZED,
					data={
						"detail": "you don't have permission to perform \
						this action, contact the admin user"
					}
				)

		if "is_superuser" in request.data:
			instance.is_superuser = request.data["is_superuser"]
		if "is_active" in request.data:
			instance.is_active = request.data['is_active']
		if "is_staff" in request.data:
			instance.is_staff = request.data['is_staff']
		instance.save()
		return Response(status=status.HTTP_200_OK, data={"detail": "user updated"})


class AdminDeleteUserView(APIView):
	"""Main super user can delete anyone and anyone can delete itself,
	put pk in url.
	"""

	permission_classes = (permissions.IsAdminUser, )

	def delete(self, request, pk, format=None):
		user = request.user
		deletable_user = get_object_or_404(User, pk=pk)
		if user.username != User.objects.filter(
			is_superuser=True,
			is_staff=True,
			is_active=True
		).first().username:
			if user != deletable_user:
				return Response(
					status=status.HTTP_400_BAD_REQUEST,
					data={"detail": "you don't have permission for this user."})

		deletable_user.is_active = False
		deletable_user.save()
		return Response(
			status=status.HTTP_200_OK,
			data={"detail": "user '{0}' deleted".format(deletable_user.username)})

# class SuggestionTicketView()
