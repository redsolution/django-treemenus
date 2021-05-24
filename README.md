# Django Tree Menus

Static multi-level menus for your Django-website.

## Requirements

- Django 2.2.*
- Python 3.5
- Django-classy-tags 0.9.0

## Installation and basic usage

1. Install package

    ``pip install git+git://github.com/oldroute/django-treemenus``

2. Configure your setting file. For example we create new menu with name "header_menu":
    
    ```python
    INSTALLED_APPS += ['treemenus']
    TREEMENUS_NAMES = {
        'header_menu':  'Header menu',
    }
    ```
    ``TREEMENUS_NAMES`` - dictionary where each record: menu-key and easy to read menu name

3. Call the menu in the html template according TREEMENUS_NAMES settings

    ```html
    {% load treemenus_tags %}
    ...
    {% show_menu 'header_menu' %}
    ```
4. Apply migrations and run local server

    ```python
    python manage.py migrate treemenus
    python manage.py runserver
    ```
5. Create "header_menu" structure in admin interface

## Advansed usage

#### Templates structure
To customize any menu template, stick to the following template structure:
- templates/
    - treemenus/
        - header_menu/
            - menu.html
            - menu_item.html
        - menu.html
        - menu_item.html

For example, when the "header_menu" is rendered, the following priority applies:
1. <PROJECT_ROOT>/templates/treemenus/header_menu/menu.html
2. <PROJECT_ROOT>/templates/treemenus/menu.html
3. treemenus/templates/treemenus/menu.html # default template from app

#### Template context

Templatetag ``{% show_menu 'header_menu' %}`` render cached menu data with template ``menu.html``

**menu.html:**
```html
{% load treemenus_tags %}

<nav>
    <ul>
        {% for item in menu.root_item.children %}
            {% show_menu_item item %}
        {% endfor %}
    </ul>
</nav>
```
``{% show_menu_item item %}`` render menu item with template ``menu_item.html``. Menu item represented as dictionary with following keys:

#### menu item attributes

- *show, has_children* - boolean;
- *caption, add_caption, url* - menuItem text and url;
- *image* - url to image (*optional*);
- *level, rank* - menuItem tree position;
- children - list of cheildren menuItems(*default: empty*).

**menu_item.html:**
```html
{% load treemenus_tags %}

<li>
    <a href="{{ item.url }}">
        {{ item.caption }}
        <img src="{{ item.image }}" alt="{{ item.caption }}" title="{{ item.caption }}">
    </a>
    {% if item.has_children %}
        <ul>
            {% for child in item.children %}
                {% show_menu_item child %} # render next level menu item
            {% endfor %}
        </ul>
    {% endif %}
</li>

```
#### Extra context

Context variables are available in the template, for example like this:

**base.html**:

```html
{% load treemenus_tags %}

<!-- desktop menu-->
{% show_menu 'header_menu' %}
...
<!-- mobile menu -->
{% with type='mobile' %}
    {% show_menu 'header_menu' %}
{% endwith %}

```
**menu.html:**
```html
{% load treemenus_tags %}

{% if type == 'mobile' %}
    <nav class='menu__mobile'> ... </nav>
{% else %}
    <nav class='menu__desktop'> ... </nav>
{% endif %}
```