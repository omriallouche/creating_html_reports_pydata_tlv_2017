# !pip install pandas
# !pip install jinja2

import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import re
import matplotlib.pyplot as plt

from gong_utils.labeling.labeler.src.html.compile import to_html

company_name = 'Realbridge'

data = pd.read_csv('sales_data1.csv')
data['amount'] = [r['amount'] if r['status']=='Won' else 0 for i,r in data.iterrows()]
data = data[data['company_name']==company_name] # Keep only records of the company of interest

# Read personal data about each sales person, like phone number, email and image
sales_people_data = pd.read_csv('sales_people_data.csv').set_index('sales_person')

agg_func_dict = {'num_deals': 'count', 'amount':'sum', 'prct_won_deals': lambda x: sum(x>0)/len(x)}
sales_by_sales_person = data.groupby('sales_person')['amount'].agg(agg_func_dict).fillna(0)

data['month'] = pd.DatetimeIndex(data['date']).month
sales_by_month = data.groupby('month')['amount'].agg(agg_func_dict).fillna(0)
# Plot bar chart, save figure as png, and pass the png filename to the template renderer
figure_amount_won_by_month = 'figure_amount_won_by_month.png'
sales_by_month['amount'].plot(kind='bar')
plt.xlabel('Month')
plt.ylabel('Sales [$]')
plt.tight_layout()
plt.savefig(figure_amount_won_by_month)
plt.close()

sales_by_industry = data.groupby('industry')['amount'].agg(agg_func_dict).fillna(0)
# Plot bar chart, this time save it as a base64 image inline the html document
import io
import urllib, base64
buf = io.BytesIO()
sales_by_industry['amount'].plot(kind='bar')
plt.tight_layout()
plt.xlabel('Industry')
plt.ylabel('Sales [$]')
plt.savefig(buf, format='png')
buf.seek(0)
string = base64.b64encode(buf.read())
figure_amount_won_by_industry = 'data:image/png;base64,' + urllib.parse.quote(string)


html_data = {
    'company_name': company_name,
    'sales_by_sales_person': sales_by_sales_person,
    'sales_people_data': sales_people_data,
    'figure_amount_won_by_industry': figure_amount_won_by_industry,
    'figure_amount_won_by_month': figure_amount_won_by_month,
    'to_html': to_html
}


report_output_filename = 'output_report_{}.html'.format(company_name)

# Set the Jinja2 environment
j2_env = Environment(loader=FileSystemLoader(os.path.abspath('.')),
                     trim_blocks=True)
# Define Jinja filters. A sample filter is: { company_name|title } which runs the function title(`company_name`) and outputs its result in the template
j2_env.filters['percent'] = lambda x: int(float(x*100))
j2_env.filters['slugify'] = lambda x: re.sub(r"[^a-zA-Z]", "", x)

template_filename = 'sales_report_template.html'
# Render the html template using actual data. We get a text string with html code
output_html = (j2_env.get_template(template_filename).render(**html_data))
# Now save the html string to file, that can be viewed in a browser
text_file = open(report_output_filename, "wt", encoding="utf8")
text_file.write(output_html)
text_file.close()

print('Report saved at '+report_output_filename)
