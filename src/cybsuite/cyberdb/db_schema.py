from cybsuite.extension import CybSuiteExtension
from koalak.descriptions import FieldDescription, SchemaDescription

from .consts import PATH_DB_SCHEMA, SSMODELS_APP_LABEL

# Tags allowed in entities
allowed_tags = [
    "knowledgebase",
    "active_directory",
    "linux_review",
    "windows_review",
    "ms_cloud",
    "web",
    "firewall",
]

# cyberdb_schema is the schema of CyberDB from all 3rd party extensions also
cyberdb_schema = SchemaDescription.from_folder(
    PATH_DB_SCHEMA,
    allowed_tags=allowed_tags,
    metadata={"django_app_label": SSMODELS_APP_LABEL},
)

# Keep track of all entities for each extension
cyberdb_entities_names_per_extension_schema: dict[str, list[str]] = {}

# Add the builtin extension
cyberdb_entities_names_per_extension_schema[SSMODELS_APP_LABEL] = list(
    e.name for e in cyberdb_schema
)

# Add 3rd party extensions
for cybsuite_extension in CybSuiteExtension.load_extensions():
    # Keep track of 3rd party extensions name / list of tables
    extension_schema = SchemaDescription.from_folder(
        cybsuite_extension.cyberdb_schema, update=False
    )
    cyberdb_entities_names_per_extension_schema[
        cybsuite_extension.cyberdb_django_app_label
    ] = list(e.name for e in extension_schema)

    # Add 3rd party extensions to main schema
    if cybsuite_extension.cyberdb_schema:
        cyberdb_schema.add_entities_from_folder(
            cybsuite_extension.cyberdb_schema,
            update=False,
            metadata={"django_app_label": cybsuite_extension.cyberdb_django_app_label},
        )


# TODO: in koalak: fix the mess for updateing schema relations(3 methods is too much)
cyberdb_schema.update_referenced_entities_from_str()
cyberdb_schema.update()
cyberdb_schema.sort()


# TODO: this lines of code are not working
for entity_description in cyberdb_schema:
    if "noteXX" in entity_description.extra:
        del entity_description.extra["note"]
        field = FieldDescription("note", type=str)
        entity_description.add_existing_field(field)

    if "sourceXX" in entity_description.extra:
        del entity_description.extra["source"]
        field = FieldDescription("source", type=str)
        entity_description.add_existing_field(field)

    if "tagsXX" in entity_description.extra:
        del entity_description.extra["tags"]
        field = FieldDescription("tags", type=str)
        entity_description.add_existing_field(field)
