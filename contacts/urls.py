from django.urls import path
from . import views

urlpatterns = [
    # Main Directory & Lifecycle
    path('', views.contact_list, name='contact_list'),
    path('edit/<int:pk>/', views.contact_update, name='contact_update'),
    path('delete/<int:pk>/', views.contact_delete, name='contact_delete'),
    path('favorite/<int:pk>/', views.contact_toggle_favorite, name='contact_toggle_favorite'),
    
    # Import / Export & vCard
    path('export/csv/', views.contact_export_csv, name='contact_export_csv'),
    path('export/sample-csv/', views.contact_download_sample_csv, name='contact_download_sample_csv'),
    path('export/vcard/<int:pk>/', views.contact_export_vcard, name='contact_export_vcard'),
    path('import/csv/', views.contact_import_csv, name='contact_import_csv'),
    path('bulk-action/', views.contact_bulk_action, name='contact_bulk_action'),

    # Epic 4: Auth & Dashboard
    path('register/', views.user_register, name='user_register'),
    path('login/', views.user_login, name='user_login'),
    path('demo-login/', views.user_demo_login, name='user_demo_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),

    # REST API (JSON)
    path('api/contacts/', views.api_contact_list_create, name='api_contact_list_create'),
    path('api/contacts/<int:pk>/', views.api_contact_detail, name='api_contact_detail'),
    path('api/contacts/stats/', views.api_contact_stats, name='api_contact_stats'),
]
