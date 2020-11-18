from datetime import date
from typing import List


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
    last_post_length: BlogCheckReport = None
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