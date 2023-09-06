# PyMYOB

[![PyPI version](https://badge.fury.io/py/pymyob.svg)](https://pypi.org/project/pymyob)
[![versions](https://img.shields.io/pypi/pyversions/pymyob.svg)](https://pypi.org/project/pymyob)
[![Downloads](https://static.pepy.tech/badge/pymyob/month)](https://pepy.tech/project/pymyob)
[![Test](https://github.com/uptick/pymyob/workflows/Test/badge.svg)](https://github.com/uptick/pymyob/actions?query=workflow%3ATest)
[![Lint](https://github.com/uptick/pymyob/workflows/Lint/badge.svg)](https://github.com/uptick/pymyob/actions?query=workflow%3ALint)

A Python API around the [MYOB Business API](https://developer.myob.com/api/myob-business-api/v2/) (formerly AccountRight Live, and New Essentials).

## Pre-getting started

Register for API Keys with MYOB. You'll find detailed instructions [here](http://developer.myob.com/api/accountright/api-overview/getting-started/).

## Getting started

Install:

```
pip install pymyob
```

Create a `PartnerCredentials` instance and provide the Key, Secret and Redirect Uri as you've set up in MYOB:

```
from myob.credentials import PartnerCredentials

cred = PartnerCredentials(
    consumer_key=<Key>,
    consumer_secret=<Secret>,
    callback_uri=<Redirect Uri>,
)
```

Cache `cred.state` somewhere. You'll use this to rebuild the `PartnerCredentials` instance later.
This object includes a datetime object, so if your cache does not serialise datetime objects, you'll need to find an alternative, such as pickling and saving to a binary database column.

Redirect the user to `cred.url`. There, they will need to log in to MYOB and authorise partnership with your app<sup id="a1">[1](#f1)</sup>. Once they do, they'll be redirected to the Redirect Uri you supplied.

At the url they're redirected to, rebuild the `PartnerCredentials` then pick the verifier out of the request and use it to verify the credentials.

```
from myob.credentials import PartnerCredentials

def myob_authorisation_complete_view(request):
    verifier = request.GET.get('code', None)
    if verifier:
        state = <cached_state_from_earlier>
        if state:
            cred = PartnerCredentials(**state)
            cred.verify(verifier)
            if cred.verified:
                messages.success(request, 'OAuth verification successful.')
            else:
                messages.error(request, 'OAuth verification failed: verifier invalid.')
        else:
            messages.error(request, 'OAuth verification failed: nothing to verify.')
    else:
        messages.error(request, 'OAuth verification failed: no verifier received.')
```

Save `cred.state` once more, but this time you want it in persistent storage. So plonk it somewhere in your database.

With your application partnered with MYOB, you can now create a `Myob` instance, supplying the verified credentials:

```
from myob import Myob
from myob.credentials import PartnerCredentials

cred = PartnerCredentials(**<persistently_saved_state_from_verified_credentials>)
myob = Myob(cred)
```

You're almost there! MYOB has this thing called company files. Even though you've authorised against a user now, you need to collect a further set of credentials for getting into the company file.

```
companyfiles = myob.companyfiles.all()

# Each company file has the following attrs:
comp.id  # Company Id
comp.name  # Company Name
comp.data  # Remaining data as a raw dict.
```
Tip: the companyfiles object specifies all supported managers (that is, endpoints).

Render a dropdown for your user to let them select which of the company files they wish to use. Usually there will only be one against their account, but best to check.
If additional authentication against the company file is needed (ie when the company file account isn't tied via SSO to a my.myob account), prompt them for the username and password for that company file and save this as follows:

```
cred.authenticate_companyfile(<company_id>, <username>, <password>)
```

Save the new `cred.state` back to your persistent storage.

Now you can access stuff!

```
from myob import Myob
from myob.credentials import PartnerCredentials

cred = PartnerCredentials(**<persistently_saved_state_from_verified_credentials>)
myob = Myob(cred)

# Obtain list of company files. Here you will also find their IDs, which you'll need to retrieve a given company file later.
company_files = myob.companyfiles.all()

# Obtain a specific company file. Use `call=False` to just prep it for calling other endpoints without actually making a call yet at this stage.
comp = myob.companyfiles.get(<company_id>, call=False)

# Obtain a list of customers (two ways to go about this).
customers = comp.contacts.all(Type='Customer')
customers = comp.contacts.customer()

# Obtain a list of sale invoices (two ways to go about this).
invoices = comp.invoices.all(InvoiceType='Item', orderby='Number desc')
invoices = comp.invoices.item(orderby='Number desc')

# Create an invoice.
comp.invoices.post_item(data=data)

# Obtain a specific invoice.
invoice = comp.invoices.get_item(uid=<invoice_uid>)

# Download PDF for a specific invoice.
invoice_pdf = comp.invoices.get_item(uid=<invoice_uid>, headers={'Accept': 'application/pdf'})

# Obtain a list of tax codes.
taxcodes = comp.general_ledger.taxcode()

# Obtain a list of inventory items.
inventory = comp.inventory.item()

# Use endswith, startswith, or substringof filters
search_text = 'Acme'
customers = comp.contacts.customer(raw_filter=f"substringof('{search_text}', CompanyName)")
```

If you don't know what you're looking for, the reprs of most objects (eg. `myob`, `comp`, `comp.invoices` above) will yield info on what managers/methods are available.
Each method corresponds to one API call to MYOB.

Note that not all endpoints are covered here yet; we've just been adding them on an as-needed basis. If there's a particular endpoint you'd like added, please feel free to throw it into the endpoints.py file and open up a PR. All contributions are welcome and will be reviewed promptly. :)

##

<a name="f1">1</a>: Your users can review their partner authorisations at https://secure.myob.com/. [↩](#a1)
