import datetime
import json
from pathlib import Path
from typing import Iterable

import django.db.models
import psycopg2
import psycopg2.sql
import yaml
from cybsuite.extension import CybSuiteExtension
from django.db.models import Model
from django.forms.models import model_to_dict
from koalak.descriptions import EntityDescription, FieldDescription, SchemaDescription
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from ..consts import SSMODELS_APP_LABEL
from .bases import AbstractDatabase, AbstractDatabaseBuilder

# TODO: now we have to specify database connection each time

DEFAULT_FORMAT = "yaml"


class DjangoORMBuilder(AbstractDatabaseBuilder):
    @classmethod
    def build(
        cls, schema: SchemaDescription, *, name: str = None, django_models
    ) -> "DjangoORMDatabase":
        if name is None:
            name = "Database"

        django_orm_database_cls = type(
            name,
            (DjangoORMDatabase,),
            {
                "schema": schema,
                "django_models": django_models,
            },
        )
        return django_orm_database_cls


class DjangoORMDatabase(AbstractDatabase):
    schema: SchemaDescription
    django_models: dict[str, Model]

    _django_alias_unique_name_counter = 0

    DATE_FORMAT = "%m-%d-%Y"

    def __init__(
        self,
        *args,
        port: int = None,
        **kwargs,
    ):
        if port is None:
            port = 5432

        super().__init__(*args, port=port, **kwargs)

        self._django_alias_db_config: str = None
        self._add_db_config_to_django(
            name=self.name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        self._django_objects: dict[str, "django.db.models.query.QuerySet"] = {}
        for model_name, model in self.django_models.items():
            self._django_objects[model_name] = model.objects.using(
                self._django_alias_db_config
            )

        self.create_database_if_not_exists()
        self._connection = psycopg2.connect(
            # "postgres" is the default database
            dbname=self.name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        self._warm_schema()

    def _add_db_config_to_django(self, *, name, user, password, host, port):
        """Dynamically add django database configuration"""
        from django.conf import settings

        cls = self.__class__
        cls._django_alias_unique_name_counter += 1

        alias_name = f"cyberdb_alias_{cls._django_alias_unique_name_counter}"
        db_config = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": name,
            "USER": user,
            "PASSWORD": password,
            "HOST": host,
            "PORT": port,
            # TODO: double check these default config!
            "ATOMIC_REQUESTS": True,
            "TIME_ZONE": "UTC",
            "CONN_HEALTH_CHECKS": True,
            "CONN_MAX_AGE": None,
            "OPTIONS": {},
            "AUTOCOMMIT": True,
        }
        settings.DATABASES[alias_name] = db_config
        django.db.connections.databases[alias_name] = db_config
        self._django_alias_db_config = alias_name

    def create_database_if_not_exists(self):
        # Connect to the PostgreSQL server to see if database exists
        connection = psycopg2.connect(
            # "postgres" is the default database
            dbname="postgres",
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        # Check if the database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            [self.name],
        )
        exists = cursor.fetchone()

        if not exists:
            # If the database doesn't exist, create it
            cursor.execute(
                psycopg2.sql.SQL("CREATE DATABASE {}").format(
                    psycopg2.sql.Identifier(self.name)
                )
            )
            self.migrate()

        cursor.close()
        connection.close()

    # ========== #
    # MIGRATIONS #
    # ========== #
    @classmethod
    def makemigrations(cls, app_labels: list[str] = None):
        """By default makes migrations in all apps (even 3rd parties)"""
        from django.core.management import call_command

        if app_labels is None:
            app_labels = [SSMODELS_APP_LABEL]
            for extension in CybSuiteExtension.load_extensions():
                app_labels.append(extension.cyberdb_django_app_label)

        call_command("makemigrations", app_labels)

    def migrate(self, app_labels: list[str] = None):
        from django.core.management import call_command

        if app_labels is None:
            app_labels = [SSMODELS_APP_LABEL]
            for extension in CybSuiteExtension.load_extensions():
                app_labels.append(extension.cyberdb_django_app_label)

        for app_label in app_labels:
            # We have to specify the database alias each time
            call_command("migrate", app_label, database=self._django_alias_db_config)

    def __getitem__(self, item):
        pass

    # ============================= #
    # Operations on rows and tables #
    # ============================= #
    def create(self, _model_name: str, **attributes):
        """Create a new entry in the database"""
        objects = self._django_objects[_model_name]
        return objects.create(**attributes)

    def feed(self, _model_name: str, _get_old_entry: bool = False, **attributes):
        """
        Args:
            _model_name: model to feed
            _get_old_entry: if True, return the old entry also
        """
        # TODO: TEST Many to many fields! ex: feed('definition', name="x", tags=['a'])
        entity = self.schema[_model_name]
        django_model = self.django_models[_model_name]
        objects = self._django_objects[_model_name]
        filter_query = {}
        cleaned_attributes = {}

        # Check all in_filter_query attributes are present
        if not entity.in_filter_query_attributes:
            raise ValueError(
                f"Can not feed the entity {entity.name} because no attribute is in_filter_query"
            )

        # Get primary attributes (in_filter_query)
        for primary_attribute in entity.in_filter_query_attributes:
            if primary_attribute.name not in attributes:
                raise ValueError(f"Required attribute '{primary_attribute.name}' ")
            filter_query[primary_attribute.name] = attributes[primary_attribute.name]

        # Geet other attributes
        for attribute_name in attributes:
            # get non primary keys
            if attribute_name not in filter_query:
                cleaned_attributes[attribute_name] = attributes[attribute_name]

        for one_to_many_field in entity.one_to_many_attributes:
            fk_name = one_to_many_field.name
            if fk_name not in attributes:
                continue
            elif isinstance(attributes[fk_name], django.db.models.Model):
                fk_instance = attributes[fk_name]
            else:
                one_to_many_field: FieldDescription
                fk_entity = one_to_many_field.type
                fk_objects = self._django_objects[fk_entity.name]
                fk_primary_attribute = fk_entity.in_filter_query_attributes
                if len(fk_primary_attribute) == 1:
                    fk_filter = {
                        fk_primary_attribute[0].name: attributes[one_to_many_field.name]
                    }
                else:
                    raise ValueError(
                        f"Fk field {entity.name}.{one_to_many_field.name} with multiple keys as primary key not handled yet"
                    )
                # TODO: must handle direct object so that we will not lose time here 34%
                fk_instance = fk_objects.update_or_create(**fk_filter)[0]
            if one_to_many_field.name in filter_query:
                filter_query[one_to_many_field.name] = fk_instance
            else:
                cleaned_attributes[one_to_many_field.name] = fk_instance

        # Handle Many to Many fields
        postponed_many_to_many_fields = {}
        for many_to_many_field in entity.many_to_many_attributes:
            many_to_many_field: FieldDescription
            if many_to_many_field.name not in cleaned_attributes:
                continue
            # TODO: the same if we have an instance isinstace(xxx, django.db.models.Model)

            fk_entity: EntityDescription = many_to_many_field.atomic_type
            if not fk_entity.is_feedable:
                raise ValueError(
                    f"{_model_name} Can not feed many_to_many relation because {entity.name} is not feedable"
                )

            if len(fk_entity.in_filter_query_attributes) != 1:
                raise ValueError(
                    f"{_model_name} Can not feed many_to_many relation because {entity.name} have more than 1 in_filter_query"
                )

            fk_field_value = cleaned_attributes[many_to_many_field.name]
            fk_model = self.django_models[many_to_many_field.atomic_type.name]
            fk_objects = self._django_objects[many_to_many_field.atomic_type.name]
            fk_primary_key_name = fk_entity.in_filter_query_attributes[0].name

            if not isinstance(fk_field_value, (list, tuple)):
                fk_field_value = [fk_field_value]

            # Convert field into real django objects
            #  ex: tags=['a', 'b'] into [Tag('a'), Tag('b')]
            postponed_many_to_many_fields[many_to_many_field.name] = [
                fk_objects.update_or_create(**{fk_primary_key_name: fk_f})[0]
                for fk_f in fk_field_value
            ]

            cleaned_attributes.pop(many_to_many_field.name)

        if _get_old_entry:
            try:
                old_entry = objects.get(**filter_query)
            except:
                old_entry = None
        # debug(filter_query, attributes, cleaned_attributes, django_model)
        new_obj, insertion_status = objects.update_or_create(
            **filter_query, defaults=cleaned_attributes
        )

        # Create postponed many to many objects associations
        for field_name, values in postponed_many_to_many_fields.items():
            # field_name could be "tags" and values [Tag1, Tag2]
            fk_many_objects = getattr(new_obj, field_name)  # ex: obj.tags
            fk_many_objects.set(values)  # control.tags.set(*[tag1, tag2])
            new_obj.save()

        if _get_old_entry:
            return new_obj, insertion_status, old_entry
        else:
            return new_obj, insertion_status

    def feed_simple(self, _model_name: str, **attributes):
        entity_description = self.schema[_model_name]
        in_filter_queries = entity_description.get_in_filter_query_attributes()
        not_in_filter_queries = entity_description.get_not_in_filter_query_attributes()
        column_names = ", ".join(attributes)
        # value_placeholders = ", ".join(["%s"] * len(attributes))
        value_placeholders = "%s, %s, %s, %s::jsonb"
        conflict_target = ", ".join(e.name for e in in_filter_queries)
        update_clause = ", ".join(
            [f"{col.name} = EXCLUDED.{col.name}" for col in not_in_filter_queries]
        )
        query = f"""
            INSERT INTO {entity_description.name} ({column_names})
            VALUES ({value_placeholders})
            ON CONFLICT ({conflict_target})
            DO UPDATE SET {update_clause};
            """

        with self._connection.cursor() as cursor:
            # Execute the query with the provided attributes as values
            cursor.execute(query, tuple(attributes.values()))
            # Commit the transaction
            self._connection.commit()

    def request(self, _model_name, **attributes) -> Iterable[dict]:
        try:
            objects = self._django_objects[_model_name]
        except:
            raise ValueError(f"No model found with the name '{_model_name}'")

        return objects.filter(**attributes)

    def first(self, _model_name, **attributes):
        try:
            objects = self._django_objects[_model_name]
        except:
            raise ValueError(f"No model found with the name '{_model_name}'")

        e = objects.filter(**attributes).first()
        if e is None:
            raise ValueError(f"No element found matching given criteria")
        return e

    def count(self, _model_name: str, **attributes) -> int:
        try:
            objects = self._django_objects[_model_name]
        except:
            raise ValueError(f"No model found with the name '{_model_name}'")

        return objects.filter(**attributes).count()

    def clear_one_model(self, model_name: str):
        try:
            objects = self._django_objects[model_name]
        except:
            raise ValueError(f"No model found with the name '{model_name}'")

        objects.all().delete()

    def cleardb(self):
        for objects in self._django_objects.values():
            objects.all().delete()

    def save_models(self, folderpath: str, _format=None, **filters):
        if _format is None:
            _format = DEFAULT_FORMAT
        elif _format not in ["json", "yaml"]:
            raise ValueError(f"unknown format {_format}")
        folderpath = Path(folderpath)
        if folderpath.exists():
            raise FileExistsError(f"Folder '{folderpath}' already exists")

        for entity in self.schema.filter(**filters):
            filepath = folderpath / entity.name / f"{entity.name}.{_format}"
            filepath.parent.mkdir(parents=True, exist_ok=True)
            self.save_one_model(entity.name, filepath, _format)

    def feed_models(self, folderpath, _format=None, **filters):
        if _format is None:
            _format = DEFAULT_FORMAT
        elif _format not in ["json", "yaml"]:
            raise ValueError(f"unknown format {_format}")
        folderpath = Path(folderpath)
        if not folderpath.exists():
            raise ValueError(f"Folder path do not exist")

        for entity in self.schema.filter(**filters):
            filepath = folderpath / entity.name / f"{entity.name}.{_format}"
            self.feed_model(entity.name, filepath)

    def feed_model(
        self, model_name: str, filepath: str, format: str = None, ignore_fields=None
    ):
        if format is None:
            format = DEFAULT_FORMAT
        elif format not in ["json", "yaml"]:
            raise ValueError(f"unknown format {format}")
        entity = self.schema[model_name]

        # Checks
        if not entity.is_feedable:
            raise ValueError(
                f"Can not load entity {entity.name}, because it is not feedable"
            )

        # Load data
        with open(filepath, "r") as f:
            if format == "json":
                data = json.load(f)
            else:
                data = yaml.safe_load(f)

        date_fields = [e.name for e in entity if e.type is datetime.date]

        for row in data:
            for field in date_fields:
                if row.get(field):
                    row[field] = datetime.datetime.strptime(
                        row[field], self.DATE_FORMAT
                    ).date()
            try:
                self.feed(model_name, **row)
            except Exception as e:
                debug(model_name, row)
                raise e

    def save_one_model(self, model_name: str, filepath: str, format: str):
        if format is None:
            format = DEFAULT_FORMAT
        elif format not in ["json", "yaml"]:
            raise ValueError(f"unknown format {format}")

        model_cls = self.django_models[model_name]
        django_objects = self._django_objects[model_name]
        entity_description = self.schema[model_name]

        # PREPARE SPECIAL FIELDS INTO LISTS #
        date_fields_names = []
        fk_fields: list[tuple[FieldDescription, str]] = []
        many_to_many_fields: list[tuple[FieldDescription, str]] = []

        for field_description in entity_description:
            # Date fields
            if field_description.type is datetime.date:
                date_fields_names.append(field_description.name)

            # Fk fields (One To Many)
            elif isinstance(field_description.atomic_type, EntityDescription):
                fk_entity_description = field_description.atomic_type
                fk_in_filter_query_fields = [
                    e for e in fk_entity_description if e.in_filter_query
                ]
                if len(fk_in_filter_query_fields) > 1:
                    raise ValueError(
                        f"Handling FK field with more than one in_filter_query is not handled yet"
                    )

                if field_description.is_set() or field_description.is_list():
                    fk_list = many_to_many_fields
                else:
                    fk_list = fk_fields

                fk_list.append((field_description, fk_in_filter_query_fields[0].name))

        data = []
        for instance in django_objects.all():
            row = model_to_dict(instance)

            # Remove 'id' key
            del row["id"]

            # convert date
            for date_field in date_fields_names:
                if row[date_field] is not None:
                    row[date_field] = row[date_field].strftime(self.DATE_FORMAT)

            # Handle simple fk field
            # Instead of saving the numeric ID, save the primary key
            #  ex instead of saving the number 5, save the name of that instance
            #  {"id": 5, "name": "alpha"}
            for fk_entity_description, fk_in_query_filter_field_name in fk_fields:
                fk_entity_name = fk_entity_description.type.name
                fk_objects = self._django_objects[fk_entity_name]
                # ex: fk_instance = ControlDefinition.objects.get(id=row['control_definition'])
                fk_instance = fk_objects.get(id=row[fk_entity_description.name])
                fk_value = getattr(fk_instance, fk_in_query_filter_field_name)
                row[fk_entity_description.name] = fk_value

            # Handle many to many
            for (
                fk_entity_description,
                fk_in_query_filter_field_name,
            ) in many_to_many_fields:
                field_name = fk_entity_description.name
                row[field_name] = [
                    getattr(e, fk_in_query_filter_field_name) for e in row[field_name]
                ]
                # Sort many to many entries (like with tags)
                row[field_name] = sorted(row[field_name])

            # Delete None and ""
            row = {k: v for k, v in row.items() if v is not None and v != ""}
            data.append(row)

        # Sort the data
        in_filter_query_attribute_names = [
            e.name for e in entity_description.get_in_filter_query_attributes()
        ]
        data.sort(key=lambda x: tuple(x[k] for k in in_filter_query_attribute_names))

        if format == "json":
            json_save(data, filepath)
        else:
            yaml_save(data, filepath)

    def get_feed_status(self, entry, inserted, old_entry):
        if inserted:
            return "new"
        if old_entry is None:
            return "existing"
        if model_to_dict(entry) == model_to_dict(old_entry):
            return "existing"
        else:
            return "updated"

    def _warm_schema(self):
        # TODO: warm schema should not be here but in koalak?
        for entity in self.schema:
            entity.in_filter_query_attributes = entity.get_in_filter_query_attributes()
            entity.one_to_many_attributes = [
                e for e in entity if isinstance(e.type, EntityDescription)
            ]
            entity.many_to_many_attributes = [
                e for e in entity if e.has_relationship() and e.is_sequence()
            ]


def json_save(obj, filepath):
    with open(filepath, "w") as file:
        json.dump(obj, file, indent=4)


def yaml_save(obj, filepath):
    with open(filepath, "w") as file:
        yaml.dump(obj, file, default_flow_style=False, indent=4)
