from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import BIN

@admin.register(BIN)
class BINAdmin(ImportExportModelAdmin):
    list_display=('id','bin_start','bin_card_type','bin_card_level','bin_card_comptype','bin_bank_name','bin_country_name',)
    pass
