from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Client, Invoice, Product, Released, Returned


class IndexView(generic.View):

    template_name = "invoice/index.html"

    def get(self, request):
        year = request.GET.get("filter_year")
        month = request.GET.get("filter_month")
        if year and month:
            invoices = Invoice.objects.filter(
                date__year=year, date__month=month
            ).order_by("-created_at")
            returned = Returned.objects.filter(
                date__year=year, date__month=month
            ).order_by("-created_at")
        else:
            invoices = Invoice.objects.order_by("-created_at")
            returned = Returned.objects.order_by("-created_at")
        clients = Client.objects.order_by("name")
        products = Product.objects.order_by("name")
        all_released = []
        for invoice in invoices:
            released = Released.objects.filter(invoice=invoice.id)
            all_released.extend(released)
            invoice.sum_qty = sum([i.qty for i in released])
            invoice.sum_summary = sum([i.summary for i in released])
        products_summary = []
        for product in products:
            filtered = [
                rel for rel in all_released if rel.product.name == product.name
            ]
            returns = returned.filter(product_id=product.id)
            sum_summary = sum([i.summary for i in filtered])
            sum_returned = sum([i.summary for i in returns])
            sum_qty = sum([i.qty for i in filtered])
            sum_returned_qty = sum([i.qty for i in returns])
            data = {
                "name": product.name,
                "sum_summary": sum_summary,
                "sum_returned": sum_returned,
                "sum_with_returned": sum_summary - sum_returned,
                "sum_qty": sum_qty,
                "sum_returned_qty": sum_returned_qty,
                "sum_with_returned_qty": sum_qty - sum_returned_qty,
            }
            products_summary.append(data)
        clients_summary = []
        for client in clients:
            filtered = [
                inv for inv in invoices if inv.client.name == client.name
            ]
            returns = returned.filter(client_id=client.id)
            sum_summary = sum([i.sum_summary for i in filtered])
            sum_returned = sum([i.summary for i in returns])
            sum_qty = sum([i.sum_qty for i in filtered])
            sum_returned_qty = sum([i.qty for i in returns])
            data = {
                "name": client.name,
                "sum_summary": sum_summary,
                "sum_returned": sum_returned,
                "sum_with_returned": sum_summary - sum_returned,
                "sum_qty": sum_qty,
                "sum_returned_qty": sum_returned_qty,
                "sum_with_returned_qty": sum_qty - sum_returned_qty,
                "sum_invoices": len(filtered),
            }
            clients_summary.append(data)
        sum_summary = sum([i.sum_summary for i in invoices])
        sum_returned = sum([i.summary for i in returned])
        context = {
            "invoices": invoices,
            "clients": clients,
            "returned": returned,
            "sum_summary": sum_summary,
            "sum_returned": sum_returned,
            "sum_with_returned": sum_summary - sum_returned,
            "products_summary": products_summary,
            "clients_summary": clients_summary,
            "returned_create_form": ReturnedCreateForm(),
            "returned_create_url": reverse("invoice:returned_create"),
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
        fields = ['product', 'qty', 'discount', 'date', 'client']


class ReturnedCreateFormView(generic.CreateView):
    model = Returned
    fields = ['product', 'qty', 'discount', 'date', 'client']

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse("invoice:index"))


class ReturnedDetailView(generic.DetailView):
    model = Returned
    template_name = "invoice/returned.html"

    def delete(self, request, pk):
        returned = get_object_or_404(Returned, pk=pk)
        returned.delete()
        return HttpResponse("OK")
