from django.db import models
import xlsxwriter
from django.apps import apps
from django.core import management
import os
import pydot
from django.http import HttpResponse


# Extracts the field props for a single field
# Could potentially pass a prop name/prop dictionary to define the order
def extract_field_props(current_field, model, field_type_dict):
    field_name = current_field.name
    field_type = type(current_field).__name__
    max_length = "NA" if current_field.max_length is None else current_field.max_length
    domain = "NA"
    if current_field.primary_key:
        help_text = model.pk_desc
    else:
        help_text = current_field.help_text

    if isinstance(current_field, models.fields.DecimalField):
        max_length = current_field.max_digits
        domain = "{} Decimals".format(current_field.decimal_places)

    c_delete = False
    c_update = False
    fk = False
    null = current_field.null
    if field_type == "ForeignKey":
        fk = True
        field_name += "_id"
        if null:
            c_update = True

    try:
        if field_type == "TextField":
            max_length = "max"
        field_type = field_type_dict[field_type]
    except KeyError:
        pass


    default = "NA" if current_field.default == models.fields.NOT_PROVIDED else current_field.default

    pk = current_field.primary_key

    blank = True if current_field.primary_key else not current_field.blank
    return [field_name, help_text, default, max_length, field_type, pk, fk, blank, null, c_delete,
            c_update, domain]


# Given a model extracts a row of field properties for each field
# Title row could be passed as a parameter
# Field_type_dict could be a parameter
def extract_all_field_props(model, field_type_dict):
    model_object = model()
    model_fields = model_object._meta.get_fields(include_parents=False)
    visible_fields = []
    output_list = []
    visible_fields = [field for field in model_fields if
                      not isinstance(field, models.fields.reverse_related.ManyToOneRel)]
    for current_field in visible_fields:
        output_row = extract_field_props(current_field, model, field_type_dict)
        output_list.append(output_row)
    return output_list


def generate_data_dict_excel(file_path, title_row, field_type_dict):
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    model_list = apps.get_app_config('Bakery').get_models()
    max_lengths = []

    for col_index, title in enumerate(title_row):
        worksheet.write(0, col_index, title, bold)
        col_length = len(str(title))
        max_lengths.append(col_length)

    row_count = 1

    for row, model in enumerate(model_list):
        model_object = model()
        model_name = model._meta.db_table
        model_desc = model_object.description
        field_props = extract_all_field_props(model, field_type_dict)
        for count, props in enumerate(field_props):
            props.append(props.pop(1))
            if count == 0:
                props.insert(0, model_name)
                props.insert(0, model.owner.name)
                props.insert(0, model.load_order)
                props.append(model_desc)
            else:
                props.insert(0, " ")
                props.insert(0, " ")
                props.insert(0, " ")
                props.append(" ")

        for field_index, field in enumerate(field_props):
            for col_index, col in enumerate(field):
                worksheet.write(row_count, col_index, col)
                col_length = len(str(col))
                if col_length > max_lengths[col_index]:
                    max_lengths[col_index] = col_length

            row_count += 1
        row_count += 1

    for index, length in enumerate(max_lengths):
        worksheet.set_column(index, index, length * 1.25)

    header_dicts = []
    for row in title_row:
        header_dicts.append({"header": row})
    worksheet.add_table(0, 0, row_count, len(title_row) - 1, {"columns": header_dicts})
    workbook.close()


def generate_erd(folder, file, shape, fields):
    module_dir = os.path.dirname(__file__)
    dot_path = os.path.join(module_dir, folder, file + ".dot")
    png_path = os.path.join(module_dir, folder, file + ".png")
    exclude_models = ["DescriptiveModel", "StatusCode", "Person", "LabelCode"]
    if fields:
        management.call_command("graph_models", "Bakery", "-o" + dot_path, disable_abstract_fields=True,
                                arrow_shape="none", exclude_models=exclude_models,
                                hide_edge_labels=True, disable_fields=True, inheritance=False)
    else:
        management.call_command("graph_models", "Bakery", "-o" + dot_path, disable_abstract_fields=True,
                                arrow_shape="none", hide_edge_labels=True)
    graphs = pydot.graph_from_dot_file(dot_path)
    graph = graphs[0]
    if shape == "crow":
        for edge in graph.get_edges():
            edge.set_arrowtail("crowodot")
            edge.set_arrowhead("teetee")

    #for node in graph.get_nodes():
        #node_name = node.get_label()
        #node.set_label(node_name)

    graph.write_png(png_path)
    response_file = open(png_path, 'rb')
    response = HttpResponse(response_file, content_type="image/png")
    return response




    

