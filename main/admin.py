from django.contrib import admin
from .models import Category, PortfolioImages, AboutMe
from account.models import Profile, Order
from booking.models import Booking


class PortfolioAdmin(admin.ModelAdmin):
	search_fields = ["title"]
	list_display = ["title", "category"]
	list_filter = [ "category"]
	class Meta:
		model = PortfolioImages


class ProfileModelAdmin(admin.ModelAdmin):
	list_display = ["username", "email", "is_allowed"]
	list_display_links = ["username","is_allowed"]
	list_filter = [ "is_allowed"]
	search_fields = ["email", "username"]
	class Meta:
		model = Profile


class OrderModelAdmin(admin.ModelAdmin):
	list_display = ["profile_name", "profile_email", "profile_amount"]
	list_display_links = ["profile_name"]
	list_filter = [ "profile_name", "date"]
	search_fields = ["profile_name"]
	class Meta:
		model = Order


admin.site.register(Category)
admin.site.register(PortfolioImages,PortfolioAdmin)
admin.site.register(Booking)
admin.site.register(AboutMe)
admin.site.register(Order,OrderModelAdmin)
admin.site.register(Profile, ProfileModelAdmin)
