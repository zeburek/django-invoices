from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Client, Invoice, Product, Released


class IndexView(generic.View):

    template_name = "invoice/index.html"

    def get(self, request):
        year = request.GET.get("filter_year")
        month = request.GET.get("filter_month")
        if year and month:
            invoices = Invoice.objects.filter(
                date__year=year, date__month=month
            ).order_by("created_at")
        else:
            invoices = Invoice.objects.order_by("-created_at")
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
            data = {
                "name": product.name,
                "sum_summary": sum([i.summary for i in filtered]),
                "sum_qty": sum([i.qty for i in filtered]),
            }
            products_summary.append(data)
        clients_summary = []
        for client in clients:
            filtered = [
                inv for inv in invoices if inv.client.name == client.name
            ]
            data = {
                "name": client.name,
                "sum_summary": sum([i.sum_summary for i in filtered]),
                "sum_qty": sum([i.sum_qty for i in filtered]),
                "sum_invoices": len(filtered),
            }
            clients_summary.append(data)
        context = {
            "invoices": invoices,
            "clients": clients,
            "sum_summary": sum([i.sum_summary for i in invoices]),
            "products_summary": products_summary,
            "clients_summary": clients_summary,
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


class InvoiceEditForm(generic.UpdateView):
    model = Invoice
    fields = ["number", "date", "client"]
    template_name_suffix = "EditForm"


class ReleasedEditForm(generic.UpdateView):
    model = Released
    fields = ["product", "qty", "discount"]
    template_name_suffix = "EditForm"
