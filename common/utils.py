def restructure_fields_by_template(object_with_fields, template_dictionary):

    existing = set(object_with_fields.fields.keys())
    allowed = set(template_dictionary.keys())

    for key in existing:
        if key in allowed:
            value = template_dictionary[key]
            if isinstance(value, dict):
                restructure_fields_by_template(object_with_fields.fields[key], value)
        else:
            object_with_fields.fields.pop(key)
