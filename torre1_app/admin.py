from django.contrib import admin

from .models import Opportunity, Company

class OpportunityAdmin(admin.ModelAdmin):
	list_display  = ['title','opportunity','company','remote','location','salary','active']
	list_editable = ['opportunity','company','remote','location','salary','active']
	class Meta:
		model = Opportunity


admin.site.register(Opportunity, OpportunityAdmin)
admin.site.register(Company)