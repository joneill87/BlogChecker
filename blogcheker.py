"""Blog-Checking Script.

This script requires a csv file containing the following columns 'Student Number', 'First Name',
'Last Name', 'Email', 'Project', 'Blog Address'. By default the script assumes this file is named BlogList.csv
The file must be in the same directory as the script. The script will ensure that each
student has a project title and blog URL listed. It will then fetch each of the blogs and output the title and date of
each student's latest blog.

Blogs must be accessible via the wordpress public api in order for this script to be able to check them.
"""

import argparse
import datetime
from datetime import date
import dateutil.parser
import requests
import pandas as pd
from mako.template import Template
from models import BlogCheckReport, BlogPost, BlogRecord
from reports import success_report, warning_report, danger_report, empty_report
import utils

parser = argparse.ArgumentParser(
    description="Perform summary check on IDSP project blogs. "
    "This script requires a csv file containing the following columns 'Student Number', 'First Name'," 
    "'Last Name', 'Email', 'Project', 'Blog Address'. By default the script assumes this file is named BlogList.csv"
    "The file must be in the same directory as the script. The script will ensure that each"
    "student has a project title and blog URL listed. It will then fetch each of the blogs and output the title and"
    "date of each student's latest blog."
)

parser.add_argument(
    "--verbose",
    action="store_true",
    help=
    "If set, the script will print the name and date of each student's last post, not just students with potential issues"
)

parser.add_argument(
    "--max-days",
    type=int,
    default=7,
    dest="max_days",
    help=
    "The maximum number of days which should have elapsed since a student's last post. Students without a post during this time period will be flagged as a warning"
)

parser.add_argument(
    "--min-post-len",
    type=int,
    default=30,
    dest="min_post_len",
    help=
    "The maximum number of days which should have elapsed since a student's last post. Students without a post during this time period will be flagged as a warning"
)

parser.add_argument("--suppress-project-check",
                    action="store_true",
                    dest="suppress_project_check",
                    help="Suppress checking with the project name is set")

parser.add_argument("--file-path",
                    type=str,
                    dest="file_path",
                    default="BlogList.csv",
                    help="Full path to csv file, relative to current directory")

args = parser.parse_args()

verbose = args.verbose
min_post_len = args.min_post_len
max_days = args.max_days
file_path = args.file_path
validate_project_name = False if args.suppress_project_check else True

api_base = "https://public-api.wordpress.com/wp/v2/sites"

min_project_name_length = 4 # helps identify projects with placeholder names like TBD

today = datetime.datetime.now().date()


def get_blog_api_url(blog_url):
    no_protocol = utils.strip_protocol_identifier(blog_url)
    return "{0}/{1}/posts?per_page=20&orderby=date&order=desc".format(
        api_base, utils.get_domain_only(no_protocol))


def check_project_name(projectname) -> BlogCheckReport:
    if not projectname or projectname.isspace():
        return danger_report("No project name specified")
    elif len(projectname) < min_project_name_length:
        return warning_report(
            "Project Name: {0} (suspiciously short)".format(projectname))
    else:
        return success_report("Project Name: {0}".format(projectname))


def check_total_posts(record) -> BlogCheckReport:
    total_posts = len(record.posts)
    if total_posts == 0:
        return danger_report("No posts")
    elif total_posts == 1:
        return warning_report("One post, only")
    else:
        return success_report("{0} post{1}".format(
            total_posts, "" if total_posts == 1 else "s"))


def check_last_post_date(record) -> BlogCheckReport:
    post_date = record.last_post_date

    if post_date is None:
        return danger_report("No posts")

    days_since_last_post = (today - post_date).days
    message = " Last Post {0} day{1} ago".format(
        days_since_last_post, "s" if days_since_last_post != 1 else "")

    if days_since_last_post > max_days:
        return warning_report(message)
    else:
        return success_report(message)


def check_last_post_length(record) -> BlogCheckReport:
    if len(record.posts) > 0:
        content = record.posts[-1].rendered
        content = utils.clean_html(content)
        tokens = content.split()
        if len(tokens) == 0:
            return warning_report("0 words in last post")
        elif 0 < len(tokens) < min_post_len:
            return warning_report(
                "last post shorter than {0} words".format(min_post_len))
        else:
            return success_report("last post OK")
    else:
        return warning_report("no last post")


def parse_blogs(api_json):
    blog_posts = list()

    for post in api_json:
        bp = BlogPost()
        bp.publish_date = dateutil.parser.parse(post['date'], ignoretz=True).date()
        bp.title = post['title']['rendered']
        bp.rendered = post['content']['rendered']
        blog_posts.append(bp)

    return blog_posts


def process_blog_column(record):
    new_line = ""
    bad_classes = ["alert alert-warning", "alert alert-danger"]
    if record.total_posts_report.css_class in bad_classes:
        new_line += "{}. ".format(record.total_posts_report.message.strip())
    if record.last_post_report.css_class in bad_classes:
        new_line +=  "{}. ".format(record.last_post_report.message.strip())
    if record.last_post_length.css_class in bad_classes:
        new_line += "{}.".format(record.last_post_length.message.strip())
    if record.blog_fetch_response_code == 403:
        new_line  = "Unauthorized access"
    if record.blog_fetch_response_code == 403:
        new_line  = "Blog not found"
    if new_line == "":
        new_line = "Blog OK"
    return new_line


def process_student(student_number, first_name, last_name, email, project_name,
                    blog_url):

    record = BlogRecord()

    print(f"{first_name} {last_name}:", end=" ")

    record.student_number = student_number
    record.last_name = last_name
    record.first_name = first_name
    record.email = email
    record.project_name = record.project_name
    record.blog_url = "https://{0}".format(utils.strip_protocol_identifier(blog_url))
    record.api_url = get_blog_api_url(record.blog_url)
    record.project_name_report = check_project_name(project_name)

    response = requests.get(record.api_url)
    record.blog_fetch_response_code = response.status_code

    if not response.status_code == 200:
        record.fetch_report = danger_report(
            "{0} error code when fetching blogs: {1}<br>{2}".format(
                response.status_code, response.text, record.api_url))
        record.last_post_report = empty_report()
        record.last_post_length = empty_report()
        record.total_posts_report = empty_report()
        record.blog_fetch_response_message = response.text
        record.posts = list()
    else:
        record.posts = parse_blogs(response.json())
        record.fetch_report = success_report("Fetched blogs successfully")
        record.last_post_report = check_last_post_date(record)
        record.last_post_length = check_last_post_length(record)
        record.total_posts_report = check_total_posts(record)

    return record


records = list()
new_column = list()

students_data = pd.read_csv(file_path, dtype='object')
students_data = students_data.fillna('')
columns_to_retrieve = [
    'Student Number', 'First Name', 'Last Name', 'Email', 'Project',
    'Blog Address'
]

for row in range(students_data.shape[0]):
    student_number, first_name, last_name, email, project_name, blog_url = students_data.iloc[
        row][columns_to_retrieve]
    if student_number:
        rec = process_student(student_number, first_name, last_name, email,
                              project_name, blog_url)
        records.append(rec)
        new_column.append(process_blog_column(rec))
        print("Done")

now = datetime.datetime.now()

with open('output_{0}.html'.format(now.strftime("%Y_%m_%d_%H_%M_%S")), 'w') as html_file:
    output = Template(filename='ReportTemplate.mako')
    html_file.write(output.render(now=str(now), records=records))

students_data['Blog {}'.format(date.today().strftime("%d/%b/%Y"))] = new_column

students_data.to_csv("BlogListUpdated.csv", index=False)

with pd.ExcelWriter("BlogListUpdated.xls") as writer:
    students_data.to_excel(writer, index=False)

print("Done")
