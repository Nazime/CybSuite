import django.db.models
from cybsuite.cyberdb.consts import SSMODELS_MODULE_NAME
from cybsuite.cyberdb.db_schema import (
    cyberdb_entities_names_per_extension_schema,
    cyberdb_schema,
)
from cybsuite.cyberdb.django_orm import DjangoORMBuilder, schema_description_to_models
from cybsuite.extension import CybSuiteExtension

"""
In order to make Django ORM works in standalone mode it's a little bit tricky.
Here are few things to know:
- In order to define models (i.e. inheriting from django.db.models.Model)
    we must first configure django settings (i.e. "django.settings.configure())
- When configuring django settings it easier to declare all apps and databases
    to avoid doing it at runtime
- In this project, apps are declared at first (by loading all apps even 3rd parties with entry_points)
    however, databases conf (with credentials username/passwords) are configured at runtime
    which makes it tricky to handle, but allows to have multiple databases at a time
    and the ability to have dynamic database conf (ex: with CLI).
"""

import django
from django.conf import settings

# Load all 3rd party extensions of cybsuite/cyberdb
extensions = CybSuiteExtension.load_extensions()

# Configure Django with all apps
# ------------------------------
if not settings.configured:
    installed_apps = [SSMODELS_MODULE_NAME]
    for extension in extensions:
        installed_apps.append(extension.cyberdb_django_app_name)

    dico_settings = {
        "INSTALLED_APPS": installed_apps,
    }

    settings.configure(**dico_settings)
    django.setup()


# Load Django models
# ------------------
# Django models are all in folders in .yaml files, which are then transformed into
# EntityDescription class, then transformed to models
# This code will models from this project and also 3rd parties extensions

django_models: dict[str, django.db.models.Model] = {}

for app_label, model_names in cyberdb_entities_names_per_extension_schema.items():
    app_models = schema_description_to_models(
        cyberdb_schema, app_label=app_label, whitelisted_models=model_names
    )
    django_models.update(app_models)

BaseCyberDB = DjangoORMBuilder.build(
    cyberdb_schema,
    name="CyberDB",
    django_models=django_models,
)
