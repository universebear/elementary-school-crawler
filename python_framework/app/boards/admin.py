from django.contrib import admin

from .models import Board, FileBoard


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    search_fields = (
        'school_name',
        'subject',
    )


@admin.register(FileBoard)
class FileBoardAdmin(admin.ModelAdmin):
    search_fields = (
        'subject',
    )
