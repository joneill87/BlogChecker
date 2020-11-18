from models import BlogCheckReport


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