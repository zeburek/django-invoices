from django import forms
from django.db.models import (
    ExpressionWrapper,
    F,
    FloatField,
    OuterRef,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from .models import Client, Invoice, Product, Released, Returned


class IndexView(generic.View):

    template_name = "invoice/index.html"

    _count_summary = ExpressionWrapper(
        F("product__price") * F("qty")
        - F("product__price") * F("qty") / 100 * F("discount"),
        output_field=FloatField(),
    )
    _invoices_sorting = ["number", "date", "created_at"]

    def _add_invoice_sorting(self, request, invoices):
        sorting = request.GET.get("sort_invoices", "-created_at")
        return invoices.order_by(sorting)

    def _generate_sorting_list(self, fields: list):
        data = []
        for field in fields:
            f = Invoice._meta.get_field(field)
            name = f.name
            vn = f.verbose_name
            data.append(
                {"value": name, "text": vn, "add_text": _("sorting_asc")}
            )
            data.append(
                {
                    "value": "-" + name,
                    "text": vn,
                    "add_text": _("sorting_desc"),
                }
            )
        return data

    def get(self, request):
        year = request.GET.get("filter_year")
        month = request.GET.get("filter_month")
        if year and month:
            invoices = Invoice.objects.filter(
                date__year=year, date__month=month
            ).all()
            returned = Returned.objects.filter(
                date__year=year, date__month=month
            ).all()
        else:
            invoices = Invoice.objects.all()
            returned = Returned.objects.all()
        invoices = self._add_invoice_sorting(request, invoices)
        returned_subquery = (
            returned.filter(product=OuterRef("pk"))
            .values("product_id")
            .annotate(
                sum_returned_qty=Sum("qty"),
                sum_returned=Sum(self._count_summary),
            )
        )
        released_subquery = (
            Released.objects.filter(
                product=OuterRef("pk"), invoice__in=invoices
            )
            .values("product_id")
            .annotate(sum_qty=Sum("qty"), sum_summary=Sum(self._count_summary))
        )
        products = Product.objects.annotate(
            sum_qty=Coalesce(
                Subquery(released_subquery.values("sum_qty")), Value(0)
            ),
            sum_summary=Coalesce(
                Subquery(released_subquery.values("sum_summary")), Value(0)
            ),
            sum_returned_qty=Coalesce(
                Subquery(returned_subquery.values("sum_returned_qty")),
                Value(0),
            ),
            sum_returned=Coalesce(
                Subquery(returned_subquery.values("sum_returned")), Value(0)
            ),
            sum_with_returned=F("sum_summary") - F("sum_returned"),
            sum_with_returned_qty=F("sum_qty") - F("sum_returned_qty"),
        ).order_by("name")

        returned_subquery = (
            returned.filter(client=OuterRef("pk"))
            .values("client_id")
            .annotate(
                sum_returned_qty=Sum("qty"),
                sum_returned=Sum(self._count_summary),
            )
        )
        released_subquery = (
            Released.objects.filter(
                invoice__client=OuterRef("pk"), invoice__in=invoices
            )
            .values("invoice__client__id")
            .annotate(sum_qty=Sum("qty"), sum_summary=Sum(self._count_summary))
        )
        clients = Client.objects.annotate(
            sum_qty=Coalesce(
                Subquery(released_subquery.values("sum_qty")), Value(0)
            ),
            sum_summary=Coalesce(
                Subquery(released_subquery.values("sum_summary")), Value(0)
            ),
            sum_returned_qty=Coalesce(
                Subquery(returned_subquery.values("sum_returned_qty")),
                Value(0),
            ),
            sum_returned=Coalesce(
                Subquery(returned_subquery.values("sum_returned")), Value(0)
            ),
            sum_with_returned=F("sum_summary") - F("sum_returned"),
            sum_with_returned_qty=F("sum_qty") - F("sum_returned_qty"),
            sum_invoices=Coalesce(Sum("invoice"), Value(0)),
        ).order_by("name")
        sum_summary = sum([i.summary for i in invoices])
        sum_returned = sum([i.summary for i in returned])
        context = {
            "invoices": invoices,
            "clients": clients,
            "returned": returned,
            "sum_summary": sum_summary,
            "sum_returned": sum_returned,
            "sum_with_returned": sum_summary - sum_returned,
            "products_summary": products,
            "returned_create_form": ReturnedCreateForm(),
            "returned_create_url": reverse("invoice:returned_create"),
            "invoice_sort_fields": self._generate_sorting_list(
                self._invoices_sorting
            ),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        client = get_object_or_404(
            Client, pk=request.POST.get("invoice_client")
        )
        try:
            data = {
                "number": int(
                    request.POST.get("invoice_number")
                    if request.POST.get("invoice_number", "") != ""
                    else 0
                ),
                "date": request.POST.get("invoice_date"),
                "client": client,
            }
        except KeyError:
            return render(
                request,
                self.template_name,
                {"error_message": "Введены неверные данные"},
            )
        else:
            invoice = Invoice(**data)
            invoice.save()
            return HttpResponseRedirect(
                reverse("invoice:details", args=(invoice.id,))
            )


class InvoiceDetailView(generic.DetailView):
    model = Invoice
    template_name = "invoice/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["released"] = Released.objects.filter(invoice=self.object.id)
        context["products"] = Product.objects.order_by("name")
        context["sum_qty"] = sum([i.qty for i in context["released"]])
        context["sum_summary"] = sum([i.summary for i in context["released"]])
        return context

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=request.POST.get("product"))
        invoice = get_object_or_404(Invoice, pk=pk)
        try:
            data = {
                "invoice": invoice,
                "product": product,
                "qty": int(
                    request.POST.get("qty")
                    if request.POST.get("qty", "") != ""
                    else 0
                ),
                "discount": int(
                    request.POST.get("discount")
                    if request.POST.get("discount", "") != ""
                    else 0
                ),
            }
        except KeyError:
            return render(
                request,
                self.template_name,
                {"error_message": "Введены неверные данные"},
            )
        else:
            released = Released(**data)
            released.save()
            return HttpResponseRedirect(reverse("invoice:details", args=(pk,)))

    def put(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        client = get_object_or_404(
            Client, pk=request.POST.get("invoice_client")
        )
        try:
            data = {
                "number": int(
                    request.POST.get("invoice_number")
                    if request.POST.get("invoice_number", "") != ""
                    else 0
                ),
                "date": request.POST.get("invoice_date"),
                "client": client,
            }
        except KeyError:
            return render(
                request,
                self.template_name,
                {"error_message": "Введены неверные данные"},
            )
        else:
            for key, value in data.items():
                setattr(invoice, key, value)
            invoice.save()
            return HttpResponseRedirect(reverse("invoice:details", args=(pk,)))

    def delete(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        invoice.delete()
        return HttpResponse("OK")


class ReleasedDetailView(generic.DetailView):
    model = Released
    template_name = "invoice/released.html"

    def delete(self, request, pk):
        released = get_object_or_404(Released, pk=pk)
        released.delete()
        return HttpResponse("OK")


class InvoiceEditFormView(generic.UpdateView):
    model = Invoice
    fields = ["number", "date", "client"]
    template_name_suffix = "EditForm"


class ReleasedEditFormView(generic.UpdateView):
    model = Released
    fields = ["product", "qty", "discount"]
    template_name_suffix = "EditForm"


class ReturnedCreateForm(forms.ModelForm):
    class Meta:
        model = Returned
        fields = ["product", "qty", "discount", "date", "client"]


class ReturnedCreateFormView(generic.CreateView):
    model = Returned
    fields = ["product", "qty", "discount", "date", "client"]

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse("invoice:index"))


class ReturnedDetailView(generic.DetailView):
    model = Returned
    template_name = "invoice/returned.html"

    def delete(self, request, pk):
        returned = get_object_or_404(Returned, pk=pk)
        returned.delete()
        return HttpResponse("OK")
