from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from .views import dict1, dict2, dict3, html_report, get_report_names, erd1
import os


class AdminTableRow:
    path = ""
    name = ""

    def __init__(self, in_path, in_name):
        self.path = in_path
        self.name = in_name


class TechSpireAdminSite(admin.AdminSite):
    site_header = "Hot Breads Admin"
    site_title = "Hot Breads Admin"
    index_title = "Welcome to Hot Breads Admin"

    #Could be improved by creating a library of reports on server start instead of everytime a link is clicked
    def index(self, request, extra_context=None):
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_list = self.get_app_list(request)
        module_dir = os.path.dirname(__file__)  # get current directory
        reports = get_report_names(module_dir)
        AdminTableRow("dict1", "Row Dictionary")
        db_info = [AdminTableRow("dict1", "Row Dictionary"), AdminTableRow("dict2", "Table Dictionary"),
                   AdminTableRow("dict3", "Excel Dictionary"), AdminTableRow("erd1", "Abstract ERD")]

        context = {
            **self.each_context(request),
            'title': self.index_title,
            'subtitle': None,
            'app_list': app_list,
            'report_list':  reports,
            'database_list': db_info,
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, self.index_template or 'admin/index.html', context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [

            path('report/<int:index>/', self.admin_view(html_report), name="report"),
            path('dict1/', self.admin_view(dict1), name="dict1"),
            path('dict2/', self.admin_view(dict2), name="dict2"),
            path('dict3/', self.admin_view(dict3), name="dict3"),
            path('erd1/', self.admin_view(erd1), name="erd1"),
        ]
        return my_urls + urls
