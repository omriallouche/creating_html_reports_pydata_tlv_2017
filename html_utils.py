#!/usr/bin/env/python
#
# Using the file system load
#
# We now assume we have a file in the same dir as this one called
# test_template.html
#

from jinja2 import Environment, FileSystemLoader
import os
from math import isnan

def to_html(df, classes='', **kwargs):
    def format_value(v, escape=False, na_rep='', float_format=None):
        if isinstance(v, float) and isnan(v):
            return na_rep
        if escape:
            from html import escape
            return escape(v)
        if float_format is not None and isinstance(v, float):
            v = float_format(v)
        return v

    rows = ''
    header = ''

    slugged_column_names = {c: slugify(c) for c in df.columns}
    header_cells = ''
    for orig_c in df.columns:
        c = slugged_column_names[orig_c]
        cell_tags = ' class="{} header" '.format(c)
        header_cells += '<th {tags}>{cell}</th>'.format(cell=format_value(c, **kwargs), tags=cell_tags)
    header = '<tr class="header">{}</tr>'.format(header_cells)

    for i, r in df.iterrows():
        cells = ''
        for j, v in r.iteritems():
            cell = v
            cell_tags = ' class="{}" '.format(slugged_column_names[j])
            cells += '<td {tags}>{cell}</td>'.format(cell=format_value(cell, **kwargs), tags=cell_tags)
        row_tags = ' class="{}" row-id={}'.format(i, i)
        row = '<tr {tags}>{cells}</tr>'.format(cells=cells, tags=row_tags)
        rows += """
            """ + row

    result = """
    <table class="{table_class}">
        <thead>{header}</thead>
        <tbody>{rows}
        </tbody>
    </table>""".format(table_class=classes, header=header, rows=rows)
    return result


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    import re
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode()
    value = (re.sub('[^\w\s-]', '', value).strip().lower())
    value = (re.sub('[-\s]+', '-', value))
    return value




def compile_html_doc(html_data_json, output_filename="index.html", filename=None):
    # Create the jinja2 environment.
    # Notice the use of trim_blocks, which greatly helps control whitespace.
    # Capture our current directory
    if filename is None:
        filename = os.path.abspath(__file__) + "/gong_template.html"
    DIR = os.path.dirname(filename)
    j2_env = Environment(loader=FileSystemLoader(DIR),
                         trim_blocks=True)
    j2_env.globals['to_html'] = to_html

    filename = os.path.basename(filename)
    output_html = (j2_env.get_template(filename).render(**html_data_json))
    text_file = open(output_filename, "wt")
    text_file.write(output_html)
    text_file.close()
    return output_html


if __name__ == '__main__':
    html_data_json = {
        'company': 'LinkedIn',
        'num_aes': 200
    }

    filename = 'template.html'
    compile_html_doc(html_data_json, filename)
