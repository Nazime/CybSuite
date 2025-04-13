import datetime
import typing

import django.utils.timezone
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import models
from koalak.descriptions import EntityDescription, SchemaDescription

_map_type_to_django_model = {
    str: models.TextField,
    int: models.IntegerField,
    float: models.FloatField,
    bool: models.BooleanField,
    dict: models.JSONField,  # Store dictionary-like data in JSON format
    typing.Dict: models.JSONField,
    bytes: models.BinaryField,  # Useful for binary data
    datetime.datetime: models.DateTimeField,  # Storing dates and times
    datetime.date: models.DateField,  # Only the date portion
    datetime.time: models.TimeField,  # Only the time portion
}

_map_default_type = {"now": django.utils.timezone.now}


banned_pretty_id_chars = EntityDescription.BANNED_PRETTY_ID_CHARS


def prett_id_validator(value):
    # TODO: double check this one!
    value = str(value)
    if any(char in value for char in banned_pretty_id_chars):
        raise ValidationError(
            f"This field should not contain any of the characters {banned_pretty_id_chars}"
        )


def schema_description_to_models(
    schema_description: SchemaDescription, *, app_label, whitelisted_models=None
):
    # app_name = name__to_appname(__name__)
    # init_django(app_name, name="secdb_blog")
    schema_description.print_warnings()
    created_models = {}
    original_app_label = app_label

    for entity_description in schema_description:
        if (
            whitelisted_models is not None
            and entity_description.name not in whitelisted_models
        ):
            continue

        pretty_id_field = entity_description.pretty_id_fields

        # Dictionary to hold all the fields for the new model
        cls_attributes = {}
        set_fields = []
        in_filter_query_fields = []

        for field_description in entity_description:
            if field_description.is_linked_by_related_name:
                continue

            if field_description.is_set():
                set_fields.append(field_description)
                # continue

            model_kwargs = {}
            model_args = []
            field_type = field_description.type
            if field_description.is_one_to_many_field():
                # TODO: here we should reference the appname also
                django_field_cls = models.ForeignKey
                django_app_label = field_description.atomic_type.metadata[
                    "django_app_label"
                ]
                model_args.append(
                    f"{django_app_label}.{field_description.atomic_type.name.title()}"
                )
                model_kwargs["on_delete"] = models.CASCADE
                model_kwargs["related_name"] = field_description.related_name
            elif field_description.is_many_to_many_field():
                django_field_cls = models.ManyToManyField
                django_app_label = field_description.atomic_type.metadata[
                    "django_app_label"
                ]
                model_args.append(
                    f"{django_app_label}.{field_description.atomic_type.name.title()}"
                )
                model_kwargs["related_name"] = field_description.related_name
            elif field_description.is_set() and field_description.atomic_type in [
                str,
                int,
            ]:
                django_field_cls = models.JSONField
            else:
                django_field_cls = _map_type_to_django_model.get(field_type)

            if django_field_cls is None:
                raise ValueError(
                    f"Unsupported type for {entity_description.name}.{field_description.name}: {field_type}"
                )

            if field_description.choices:
                choices = [(e, e) for e in field_description.choices]
                model_kwargs["choices"] = choices
            if field_description.unique:
                model_kwargs["unique"] = field_description.unique
            if (
                field_description.nullable
                and not field_description.is_many_to_many_field()
            ):
                model_kwargs["null"] = True
                model_kwargs["blank"] = True
            elif field_description.is_many_to_many_field():
                model_kwargs["blank"] = True
            elif field_description.default in _map_default_type:
                model_kwargs["default"] = _map_default_type[field_description.default]
            elif field_description.default:
                model_kwargs["default"] = field_description.default
            if field_description.indexed:
                model_kwargs["db_index"] = True
            if (
                field_description.is_one_to_many_field()
                and field_description.related_name
            ):
                model_kwargs["related_name"] = field_description.related_name

            if field_description.in_filter_query:
                in_filter_query_fields.append(field_description.name)

            if field_description.name in pretty_id_field:
                # Add the `pretty_id_validator` function to the field `validators` argument
                model_kwargs["validators"] = [prett_id_validator]

            try:
                django_field = django_field_cls(*model_args, **model_kwargs)
            except Exception as e:
                debug(django_field_cls, model_args, model_kwargs)
                raise e
            # Add each field to the model's fields dictionary
            cls_attributes[field_description.name] = django_field

        # Define a Meta class with optional settings
        unique_constraints = []
        if in_filter_query_fields:
            unique_constraints.append(
                models.UniqueConstraint(
                    fields=in_filter_query_fields,
                    name=f'unique_{entity_description.name}.{"_".join(in_filter_query_fields)}',
                )
            )

        for unique_fields in entity_description.unique:
            if isinstance(unique_fields, list):
                unique_constraints.append(
                    models.UniqueConstraint(
                        fields=unique_fields,
                        name=f'unique_{entity_description.name}.{"_".join(unique_fields)}',
                    )
                )

        class Meta:
            db_table = entity_description.name  # FIXME: this is not working, dunno why
            verbose_name_plural = entity_description.name
            verbose_name = entity_description.name.removesuffix("s")
            constraints = unique_constraints
            app_label = original_app_label

        repr_fields = [e.name for e in entity_description if e.repr]
        if not repr_fields:
            repr_fields = ["id"]

        # Add the `__str__` method to the model's attributes
        cls_attributes["__str__"] = build__str__(repr_fields)

        # Add the Meta class to the attributes of the new model
        cls_attributes["Meta"] = Meta
        cls_attributes["__module__"] = __name__

        # Dynamically create the new model class
        new_class_name = entity_description.name.title()
        new_class = type(new_class_name, (models.Model,), cls_attributes)

        # Store the new class in the dictionary
        created_models[entity_description.name] = new_class

    return created_models


def build__str__(repr_fields):
    if len(repr_fields) == 1:

        def __str__(self):
            return str(getattr(self, repr_fields[0]))

        return __str__

    def __str__(self):
        return " - ".join(f"{getattr(self, field)}" for field in repr_fields)
        # return ", ".join(f"{field}: {getattr(self, field)}" for field in repr_fields)

    return __str__
