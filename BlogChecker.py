"""Blog-Checking Script.

This script requires a csv file named in the format <student name>, <project title>, <blog URL> (additional columns ignored).
This file should contain a header row. The file must be in the same directory as the script. The script will ensure that each
student has a project title and blog URL listed. It will then fetch each of the blogs and output the title and date of
each student's latest blog.

Blogs must be accessible via the wordpress public api in order for this script to be able to check them.
"""

import argparse
import csv
import datetime
import dateutil.parser
import re
import requests

from typing import List
from datetime import date
from mako.template import Template


class BlogCheckReport:
    message: str = None
    css_class: str = None


class BlogPost:
    title: str = None
    publish_date: date = None
    rendered: str = None


class BlogRecord:
    first_name: str = None
    last_name: str = None
    student_number: str = None
    email: str = None
    project_name: str = None
    public_blog_url: str = None
    blog_api_url: str = None
    blog_fetch_response_code: int = None
    blog_fetch_response_message: str = None
    fetch_report: BlogCheckReport = None
    last_post_report: BlogCheckReport = None
    total_posts_report: BlogCheckReport = None
    project_name_report: BlogCheckReport = None
    posts: List[BlogPost] = list()

    @property
    def post_count(self):
        return len(self.posts)

    @property
    def last_post_date(self):
        return None if len(self.posts) == 0 else \
            sorted(self.posts, key=lambda post: post.publish_date, reverse=True)[0].publish_date


parser = argparse.ArgumentParser(description="Perform summary check on IDSP project blogs. "
                                             "This script requires a csv file in the format <student number>, <first name>, <last name>, <email>, <project title>, <blog URL> (additional columns ignored)."
                                             "The script will ensure that each student has a project title and blog URL listed. It will then fetch each of the "
                                             "blogs using the wordpress API and output the title and date of each student's latest blog. "
                                             "Blogs must be accessible via the wordpress public api in order for this script to be able to check them. "
                                 )
parser.add_argument("--verbose", action="store_true",
                    help="If set, the script will print the name and date of each student's last post, not just students with potential issues")
parser.add_argument("--max-days", type=int, default=7, dest="max_days",
                    help="The maximum number of days which should have elapsed since a student's last post. Students without a post during this time period will be flagged as a warning")
parser.add_argument("--suppress-project-check", action="store_true", dest="suppress_project_check",
                    help="Suppress checking with the project name is set")
parser.add_argument("--file-path", type=str, dest="file_path", default="BlogList.csv",
                    help="Full path to csv file, relative to current directory")
args = parser.parse_args()

verbose = args.verbose
max_days = args.max_days
file_path = args.file_path
validate_project_name = False if args.suppress_project_check else True

# Globals
standard_color = "grey"
error_color = "red"
warning_color = "yellow"
happy_color = "green"

api_base = "https://public-api.wordpress.com/wp/v2/sites"

min_project_name_length = 4

today = datetime.datetime.now().date()


def danger_report(message):
    report = BlogCheckReport()
    report.css_class = "alert alert-danger"
    report.message = message
    return report


def warning_report(message):
    report = BlogCheckReport()
    report.css_class = "alert alert-warning"
    report.message = message
    return report


def success_report(message):
    report = BlogCheckReport()
    report.css_class = "alert alert-success"
    report.message = message
    return report


def empty_report():
    report = BlogCheckReport()
    report.css_class = "invisible"
    report.message = ""
    return report


def strip_protocol_identifier(url) -> str:
    return re.sub("http[s]?\:\/\/", "", url)


def get_domain_only(url) -> str:

    if ".com" in url:
        return url[0:url.index('.com')] + '.com'.strip('/')
    else:
        return url.strip('/')


def get_blog_api_url(blog_url):
    no_protocol = strip_protocol_identifier(blog_url)
    return "{0}/{1}/posts?per_page=20".format(api_base, get_domain_only(no_protocol))


def check_project_name(projectname) -> BlogCheckReport :
    if not projectname or projectname.isspace():
        return danger_report("No project name specified")
    elif len(projectname) < min_project_name_length:
        return warning_report("Project Name: {0} (suspiciously short)".format(projectname))
    else:
        return success_report("Project Name: {0}".format(projectname))


def check_total_posts(record) -> BlogCheckReport :
    total_posts = len(record.posts)
    if total_posts == 0:
        return danger_report("No posts")
    elif total_posts == 1:
        return warning_report("One post, only")
    else:
        return success_report("{0} post{1}".format(total_posts, "" if total_posts == 1 else "s"))


def check_last_post_date(record) -> BlogCheckReport :
    post_date = record.last_post_date

    if post_date is None:
        return danger_report("No posts")

    days_since_last_post = (today - post_date).days
    message = " Last Post {0} day{1} ago".format(
        days_since_last_post,
        "s" if days_since_last_post != 1 else "")

    if days_since_last_post > max_days:
        return warning_report(message)
    else:
        return success_report(message)


def parse_blogs(api_json):
    blog_posts = list()

    for post in api_json:
        bp = BlogPost()
        bp.publish_date = dateutil.parser.parse(post['date'], ignoretz=True).date()
        bp.title = post['title']['rendered']
        bp.rendered = post['content']['rendered']
        blog_posts.append(bp)

    return blog_posts


def process_student(student_number, first_name, last_name, email, project_name, blog_url):
    global console_message
    console_message = ""

    record = BlogRecord()

    valid = False
    print(f"{first_name} {last_name}:", end=" ")

    record.last_name = last_name
    record.first_name = first_name
    record.email = email
    record.project_name = record.project_name
    record.blog_url = "https://{0}".format(strip_protocol_identifier(blog_url))
    record.api_url = get_blog_api_url(record.blog_url)
    record.project_name_report = check_project_name(project_name)

    response = requests.get(record.api_url)
    record.blog_fetch_response_code = response.status_code

    if not response.status_code == 200:
        record.fetch_report = danger_report("{0} error code when fetching blogs: {1}<br>{2}".format(
            response.status_code, response.text, record.api_url))
        record.last_post_report = empty_report()
        record.total_posts_report = empty_report()
        record.blog_fetch_response_message = response.text
        record.posts = list()
    else:
        record.posts = parse_blogs(response.json())
        record.fetch_report = success_report("Fetched blogs successfully")
        record.last_post_report = check_last_post_date(record)
        record.total_posts_report = check_total_posts(record)

    return record


records = list()

with open(file_path) as file:
    reader = csv.reader(file, delimiter=',')
    next(reader, None)

    for row in reader:
        student_number, first_name, last_name, email, project_name, blog_url = row[0:6]
        if student_number:
            rec = process_student(student_number, first_name, last_name, email, project_name, blog_url)
            records.append(rec)
            print("Done")

    now = datetime.datetime.now()

    with open('output_{0}.html'.format(now.strftime("%Y_%m_%d_%H_%M_%S")), 'w') as html_file:
        output = Template(filename='ReportTemplate.mako')
        html_file.write(output.render(now=str(now), records=records))

print("Done")
