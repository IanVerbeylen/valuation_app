from django.contrib import admin

from .models import Portfolio, Company

# Register your models here.


class CompanyInline(admin.TabularInline):
    model = Company
    extra = 3


class PortfolioAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["portfolio_name"]}),
        ("Date Information", {"fields": ["creation_date"]}),
    ]
    inlines = [CompanyInline]
    list_display = ("portfolio_name", "creation_date", "was_created_recently")
    list_filter = ["creation_date"]
    search_fields = ["portfolio_name"]


admin.site.register(Portfolio, PortfolioAdmin)
