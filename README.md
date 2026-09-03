# Food Menu App — Django & DRF Practice Reference

A food menu application built to practice **Django and Django REST Framework**. This repository doubles as my personal **syntax reference**: a place to quickly revisit patterns, compare approaches, and find examples in working project files.

> **Learning project, not a production restaurant or ordering system.** Some alternative implementations are intentionally preserved as comments. The examples below distinguish active behavior from study patterns and proposed improvements. See [Known limitations](#known-limitations) before reusing the code.

## Quick navigation

| I want to remember… | Jump to |
| --- | --- |
| Setup and everyday commands | [Run locally](#run-locally) · [Command cheat sheet](#command-cheat-sheet) |
| Fields, relationships, queries, managers | [Models and ORM](#models-and-orm) |
| Soft deletion | [Soft delete](#soft-delete) |
| Forms, uploads, validation | [Forms](#forms) |
| Function views vs class-based views | [Django views](#django-views) |
| Templates, filters, caching | [Templates and caching](#templates-and-caching) |
| Serializers and validation | [Serializers](#serializers) |
| Nested API output | [Nested serializers](#nested-serializers) |
| ViewSets and routers | [ViewSets and routing](#viewsets-and-routing) |
| JWT and owner permissions | [Authentication and permissions](#authentication-and-permissions) |
| Search, ordering, pagination, throttling | [API query controls](#api-query-controls) |
| API URLs and curl examples | [API reference](#api-reference) |
| Middleware and logging | [Middleware and logging](#middleware-and-logging) |
| What still needs work | [Known limitations](#known-limitations) |

## What this project practices

- Server-rendered menu pages, forms, registration, login, logout, and a profile page.
- Item CRUD, creator relationships, image fields, and soft deletion in the web delete view.
- PostgreSQL, custom managers, indexes, and model relationships.
- DRF serializers, nested representations, validation, ViewSets, and routers.
- JWT authentication, object-level permissions, search, ordering, pagination, and throttling.
- OpenAPI schema generation, Swagger UI, and ReDoc with drf-spectacular.
- Tailwind CSS, custom template filters, caching experiments, middleware, and logging.

The food menu is the exercise domain; the main goal is learning and comparing implementation patterns.

## Project map

| Location | Purpose |
| --- | --- |
| [base/models.py](base/models.py) | `Item`, `Category`, and `Order` |
| [base/managers.py](base/managers.py) | Filtered default manager and reusable queries |
| [base/views.py](base/views.py) | Active web views and API ViewSets; commented alternatives |
| [base/forms.py](base/forms.py) | Item form and form validation |
| [base/serializers.py](base/serializers.py) | Item, user, and order representations |
| [base/permissions.py](base/permissions.py) | Owner-only object writes |
| [base/urls.py](base/urls.py) | Web routes, API router, JWT routes |
| [base/middlewares.py](base/middlewares.py) | Request logging, timing, and IP-blocking exercise |
| [base/templatetags/custom_filters.py](base/templatetags/custom_filters.py) | Currency and discount filters |
| [users/](users/) | Registration, authentication pages, and profile model |
| [theme/](theme/) | Shared templates and Tailwind source |
| [foodmenuapp/settings.py](foodmenuapp/settings.py) | Database, middleware, cache, logging, DRF settings |
| [foodmenuapp/urls.py](foodmenuapp/urls.py) | Main URL configuration and API docs |

## Run locally

The supplied requirements pin Django `6.1`, DRF `3.18.0`, django-tailwind `4.5.0`, Simple JWT `5.5.1`, and drf-spectacular `0.30.0`. These are repository pins, not a claim that every dependency combination has been independently tested. Use a Python version compatible with those pins and a running PostgreSQL instance.

From the directory containing `manage.py`:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a PostgreSQL database and role, then create a local `.env` file with your own values:

```dotenv
DB_NAME=foodmenuapp
DB_USER=your_database_user
DB_PASSWORD=your_local_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

The database credentials and Django secret key are loaded from a local .env file using python-dotenv. This file must not be committed to version control.

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

In another terminal, activate the same environment and start the CSS watcher:

```bash
python manage.py tailwind start
```

Alternatively, the repository's `Procfile.tailwind` starts both processes:

```bash
honcho -f Procfile.tailwind start
```

Open [the local app](http://127.0.0.1:8000/) and sign in. Use [Django admin](http://127.0.0.1:8000/admin/) to create sample records and orders. These commands are source-based setup instructions; they have not been verified against a fresh database as part of this README preparation.

## Command cheat sheet

```bash
# Model changes
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations

# Interactive ORM
python manage.py shell

# Checks and tests — test files currently contain no test cases
python manage.py check
python manage.py test

# Python / template formatting
ruff check .
ruff format .
djlint base/templates users/templates theme/templates --reformat

# Generate API schema
python manage.py spectacular --file schema.yml --validate

# Compile CSS once
python manage.py tailwind build
```

## Models and ORM

Source: [models](base/models.py) · [managers](base/managers.py) · [profile model](users/models.py).

Relationship syntax used in the project:

```python
# One user → many orders
user = models.ForeignKey(User, on_delete=models.CASCADE)

# Many orders ↔ many items
items = models.ManyToManyField(Item, related_name="orders")

# One user ↔ one profile
user = models.OneToOneField(User, on_delete=models.CASCADE)

# Other field patterns
item_price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
item_image = models.ImageField(upload_to="item_images", blank=True, null=True)
created_at = models.DateTimeField(auto_now_add=True)
```

`Category` currently exists independently; `Item` has no category foreign key.

Shell reference — replace `1` with an existing record ID:

```python
from base.models import Item, Order

Item.objects.all()                         # Call all(), not all
Item.objects.filter(item_price__lt=10)
Item.objects.filter(item_name__icontains="pizza")
Item.objects.order_by("item_price")
Item.objects.order_by("-created_at")
Item.objects.cheap_items()                 # Price < 2
Item.objects.expensive_items()             # Price > 10
Item.objects.search("pizza")               # Name contains keyword
Item.objects.deleted()                     # Soft-deleted records

item = Item.objects.get(pk=1)
item.orders.all()                          # Reverse M2M relation
order = Order.objects.get(pk=1)
order.items.all()
```

For an M2M write, save the order first, then use `order.items.add(item)` or `order.items.set(items)`. `pk` refers to the model's primary key without assuming its field name.

## Soft delete

Active model method:

```python
def soft_delete(self, using=None, keep_parents=True):
    self.is_deleted = True
    self.deleted_at = timezone.now()
    self.save(update_fields=["is_deleted", "deleted_at"])
```

The custom manager hides flagged items by default:

```python
def get_queryset(self):
    return super().get_queryset().filter(is_deleted=False)

def deleted(self):
    return super().get_queryset().filter(is_deleted=True)
```

**Important:** the web delete view calls `soft_delete()`. DRF's current default destroy action calls `delete()` and therefore hard-deletes. The model does not override `delete()`.

## Forms

Source: [base/forms.py](base/forms.py).

```python
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ("item_name", "item_description", "item_price", "item_image")

    def clean_item_price(self):
        price = self.cleaned_data["item_price"]
        if price < 0:
            raise forms.ValidationError("Price cannot be negative")
        return price
```

`clean_<field>()` validates one field; `clean()` compares fields. The current form rejects descriptions containing the item name, case-insensitively. That differs from the serializer's equality check.

**Improvement pattern, not the current create view:** when handling uploaded files and setting ownership:

```python
form = ItemForm(request.POST or None, request.FILES or None)
if request.method == "POST" and form.is_valid():
    item = form.save(commit=False)
    item.creator = request.user
    item.save()
```

The HTML form must use `method="post"`, `enctype="multipart/form-data"`, and `{% csrf_token %}`. The supplied create view does not bind `request.FILES` or set the creator, and its image widget is still a `URLInput` from the earlier URL-field implementation.

## Django views

Source: [base/views.py](base/views.py).

Active function-based view pattern:

```python
@login_required
def detail(request, pk):
    item = get_object_or_404(Item, id=pk)
    return render(request, "base/detail.html", {"item": item})
```

Active class-based update pattern:

```python
class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    fields = ("item_name", "item_description", "item_price", "item_image")
    template_name = "base/item_form.html"
    login_url = "users/login"

    def get_queryset(self):
        return Item.objects.filter(creator=self.request.user)
```

Filtering the queryset limits which objects the view can retrieve. The source also retains **commented** `ListView`, `DetailView`, `CreateView`, and `DeleteView` experiments. They are alternatives, not additional active routes.

HTML pagination:

```python
paginator = Paginator(Item.objects.all(), per_page=5)
page_object = paginator.get_page(request.GET.get("page"))
```

## Templates and caching

Source: [home template](base/templates/base/home.html) · [filters](base/templatetags/custom_filters.py).

```django
{% extends "base.html" %}
{% load custom_filters %}
{% block content %}
    {% for item in page_object %}
        <a href="{% url 'base:detail' item.pk %}">{{ item.item_name }}</a>
        <p>{{ item.item_price|floatformat:2|currency }}</p>
    {% endfor %}
{% endblock %}
```

Register a custom filter:

```python
from django import template
register = template.Library()

@register.filter
def currency(price):
    return f"Price: ${price}"
```

The `currency` filter adds a label; `floatformat:2` supplies the two decimal places in the template.

File-based caching is configured, but the view-cache decorators and home-page fragment-cache tags are **commented out**. Syntax to revisit:

```django
{% load cache %}
{% cache 900 item item.pk %}
    <p>{{ item.item_name }}</p>
{% endcache %}
```

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)
def example_view(request):
    ...
```

Fragment caching caches part of the rendered template, not the whole HTTP response. Include appropriate variation in cache keys before caching user-specific output.

## Serializers

Source: [base/serializers.py](base/serializers.py).

Active field-level validation:

```python
def validate_item_price(self, value):
    if value < 0:
        raise serializers.ValidationError("Price must be greater than 0.")
    return value
```

The condition permits zero despite the message saying “greater than 0.”

Active object-level validation:

```python
def validate(self, attrs):
    if attrs["item_name"] == attrs["item_description"]:
        raise serializers.ValidationError("Name and Description must be different.")
    return attrs
```

**PATCH caveat:** omitted fields are not necessarily in `attrs`. The current implementation can raise `KeyError` during partial updates. An improvement pattern is to fall back to the existing instance:

```python
def validate(self, attrs):
    name = attrs.get("item_name", getattr(self.instance, "item_name", None))
    description = attrs.get(
        "item_description", getattr(self.instance, "item_description", None)
    )
    if name is not None and name == description:
        raise serializers.ValidationError("Name and Description must be different.")
    return attrs
```

## Nested serializers

Active relationships in [base/serializers.py](base/serializers.py):

```python
# On ItemSerializer:
creator = UserSerializer(read_only=True)

# On OrderSerializer:
items = ItemSerializer(many=True, read_only=True)
user = serializers.StringRelatedField()
```

- `many=True`: serialize a collection.
- `read_only=True`: include the relationship in output, not writable input.
- `StringRelatedField`: read-only representation using the related object's `__str__`.

Orders embed item data, and items embed creator data. **Nested output does not implement nested creation.** The order serializer cannot currently accept a user or item IDs to create a complete order through the API.

## ViewSets and routing

Active item ViewSet, shortened from [base/views.py](base/views.py):

```python
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
```

Router syntax from [base/urls.py](base/urls.py):

```python
router = DefaultRouter()
router.register(r"items", views.ItemViewSet, basename="item")
router.register(r"orders", views.OrderViewSet, basename="order")

urlpatterns = [path("api/", include(router.urls))]
```

Study progression retained in the source:

| Approach | Main syntax | Status |
| --- | --- | --- |
| Function-based API | `@api_view(["GET", "POST"])` | Commented |
| APIView | `class ItemListCreateAPIView(APIView)` | Commented |
| Generic views | `generics.ListCreateAPIView` | Commented |
| ViewSet + router | `viewsets.ModelViewSet` | Active |

## Authentication and permissions

The web UI uses Django sessions; the API uses JWT. A browser login alone does not authenticate requests to the JWT-only API configuration.

Object permission in [base/permissions.py](base/permissions.py):

```python
def has_object_permission(self, request, view, obj):
    if request.method in permissions.SAFE_METHODS:
        return True
    return obj.creator == request.user
```

The item API combines two permission classes:

- `IsAuthenticatedOrReadOnly`: allows public reads but requires authentication for writes.
- `IsOwnerOrReadOnly`: restricts updates and deletions to the item's creator.

```python
from rest_framework.permissions import IsAuthenticatedOrReadOnly

permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
```

Object-level permissions do not check creation. `IsAuthenticatedOrReadOnly` guards POST requests, while `perform_create()` assigns the authenticated user as the creator.

The order API requires authentication and restricts access to the user's own orders:

```python
from rest_framework.permissions import IsAuthenticated

permission_classes = (IsAuthenticated,)

def get_queryset(self):
    return Order.objects.filter(user=self.request.user)

def perform_create(self, serializer):
    serializer.save(user=self.request.user)
```

Filtering `get_queryset()` scopes listing, retrieval, updates, and deletion to orders owned by the authenticated user.

**Current limitation:** nested order items remain read-only. Assigning the order's owner does not implement adding items through the API.

## API query controls

Active item settings:

```python
filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
search_fields = ("item_name", "item_price")
throttle_classes = (AnonRateThrottle, UserRateThrottle)
```

| Example | Purpose |
| --- | --- |
| `/api/items/?search=pizza` | Search configured fields |
| `/api/items/?ordering=item_price` | Ascending price |
| `/api/items/?ordering=-item_price` | Descending price |
| `/api/items/?limit=5&offset=10` | Skip 10 results, return up to 5 |
| `/api/items/?search=pizza&ordering=item_price&limit=5` | Combine controls |

`filterset_fields` and `ordering_fields` are commented out. Installing `DjangoFilterBackend` alone does not activate exact field filters such as `?item_name=pizza`.

Global settings in [settings.py](foodmenuapp/settings.py):

```python
"DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
"PAGE_SIZE": 10,
"DEFAULT_THROTTLE_RATES": {"anon": "10/minute", "user": "1000/day"},
```

The HTML list uses five records per page; the API defaults to ten. Throttling uses the configured cache and is a practice rate limit, not a complete abuse-prevention system.

## API reference

Paths below match the supplied URL configuration, including trailing-slash differences.

| URL | Methods / purpose | Current caveat |
| --- | --- | --- |
| `/api/` | GET router index | — |
| `/api/items/` | GET, POST | POST needs a valid JWT to assign a creator; explicit create permission is missing |
| `/api/items/<id>/` | GET, PUT, PATCH, DELETE | Owner writes; PATCH validation needs improvement; DELETE is hard delete |
| `/api/orders/` | GET, POST | List is exposed; complete order creation is not implemented |
| `/api/orders/<id>/` | GET, PUT, PATCH, DELETE | No ownership restrictions; nested relationships are read-only |
| `/api/token/` | POST username/password | Returns access and refresh tokens |
| `/api/token/refresh` | POST refresh token | **No trailing slash** in current route |
| `/api/schema/` | GET OpenAPI schema | Generated by drf-spectacular |
| `/api/schema/swagger-ui/` | GET Swagger UI | Interactive documentation |
| `/api/schema/redoc/` | GET ReDoc | Readable API documentation |

### Request examples

All credentials below are placeholders. Use only local test accounts and data.

```bash
# Obtain JWTs
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"your_username","password":"your_password"}'

# Search items
curl 'http://127.0.0.1:8000/api/items/?search=pizza&limit=5'

# Create an item; replace the token placeholder
curl -X POST http://127.0.0.1:8000/api/items/ \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"item_name":"Pizza","item_description":"Tomato and mozzarella","item_price":"12.50"}'

# Refresh an access token
curl -X POST http://127.0.0.1:8000/api/token/refresh \
  -H 'Content-Type: application/json' \
  -d '{"refresh":"YOUR_REFRESH_TOKEN"}'
```

The schema advertises router-generated methods; that does not establish that every write workflow is complete or secure.

## Middleware and logging

Source: [middleware](base/middlewares.py) · [settings](foodmenuapp/settings.py).

```python
class TimerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        print(f"[Middleware] Request took: {duration:.2f} seconds")
        return response
```

Code before `get_response(request)` runs on the incoming path; code after it runs when the response returns. The project also prints request paths/statuses and includes a simple IP-blocking exercise.

View logging pattern:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Fetching all items from the database")
```

The current logging configuration writes to the console and `debug.log` at DEBUG level. Logs can contain request and user information.

## Known limitations

This is a learning project. The following areas remain incomplete or need improvement:

- **Deployment settings:** `DEBUG=True` and local host settings are intended for development and must be adjusted before deployment.
- **Web delete permissions:** the web delete view requires login but does not yet verify item ownership.
- **Web item creation:** the create view does not assign the authenticated user as the creator. The model currently defaults to user ID `1`.
- **Image uploads:** the item form still uses a URL widget, the create view does not handle `request.FILES`, and the template lacks multipart encoding.
- **Partial updates:** serializer validation directly accesses fields that may be absent in PATCH requests.
- **Deletion behavior:** the web interface uses soft deletion, while the API uses hard deletion. These behaviors need a consistent policy.
- **Order items:** orders are restricted to their owners, and ownership is assigned on creation. However, nested items remain read-only, so adding or changing order items through the API is not implemented.
- **Profiles:** registration does not automatically create a related `Profile` record.
- **Caching:** a cache backend is configured, but the view-level and template-fragment caching examples are currently disabled.
- **Tests:** the app test files are placeholders; automated tests have not yet been implemented.

Order quantities, price snapshots, checkout, and payments are outside the current scope of this syntax-practice project.

---

**How I use this repository:** find a topic in the quick-navigation table, copy the small syntax pattern, then open its linked source file for the surrounding implementation. Study examples are a starting point, not a substitute for validation, tests, or access-control review.
