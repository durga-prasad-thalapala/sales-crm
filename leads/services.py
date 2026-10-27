from django.db import transaction

from customers.models import Customer

from .models import Lead


@transaction.atomic
def convert_lead_to_customer(lead_id):
    lead = Lead.objects.select_for_update().get(id=lead_id)

    if lead.status != Lead.Status.QUALIFIED:
        raise ValueError("Only qualified leads can be converted.")

    if lead.converted_customer_id:
        raise ValueError("This lead has already been converted.")


    customer = Customer.objects.create(
        name=lead.name,
        company=lead.company,
        email=lead.email,
        phone=lead.phone,
        created_by=lead.assigned_to,
    )


    lead.converted_customer = customer
    lead.status = Lead.Status.CONVERTED
    lead.save(update_fields=["converted_customer", "status", "updated_at"])

    return customer
