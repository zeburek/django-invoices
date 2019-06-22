from django.urls import path

from . import views

app_name = "invoice"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.InvoiceDetailView.as_view(), name="details"),
    path(
        "<int:pk>/edit", views.InvoiceEditForm.as_view(), name="edit_invoice"
    ),
    path(
        "released/<int:pk>/",
        views.ReleasedDetailView.as_view(),
        name="released_details",
    ),
    path(
        "released/<int:pk>/edit",
        views.ReleasedEditForm.as_view(),
        name="released_edit",
    ),
]
