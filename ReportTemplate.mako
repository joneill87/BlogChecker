<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Blog Check ${now}</title>

    <link rel="stylesheet" type="text/css" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"
            integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo"
            crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"
            integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1"
            crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"
            integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM"
            crossorigin="anonymous"></script>

    <style>
        .collapse-trigger {
            cursor: pointer;
        }

        .blog-check-alerts {
            float: right;
            width: 65%;
        }
        .blog-check-details {
            width: 35%;
        }
    </style>
</head>
<body>
<div class="accordion" id="blogAccordion">
    % for record in records:
          <section class="card">
            <div class="card-header" id="blog${loop.index}">
                <div class="blog-check-alerts">
                    <div class="${record.project_name_report.css_class}">
                        ${record.project_name_report.message}
                    </div>
                     <div class="${record.fetch_report.css_class}">
                        ${record.fetch_report.message}
                    </div>
                     <div class="${record.last_post_report.css_class}">
                        ${record.last_post_report.message}
                    </div>
                     <div class="${record.total_posts_report.css_class}">
                        ${record.total_posts_report.message}
                    </div>
                </div>

                <div class="blog-check-details">
                     <h1 class="collapse-trigger" id="headerBloggerName${loop.index}">
                        <a data-toggle="collapse" data-target="#blogger${loop.index}"
                           aria-expanded="true" aria-controls="blogger${loop.index}">
                            ${record.first_name} ${record.last_name}
                        </a>
                    </h1>
                    <div>
                        <a href="${record.blog_url}">${record.blog_url}</a>
                    </div>
                    <p>${record.first_name} has ${record.post_count} post(s)</p>
                    <p>Last post was ${record.last_post_date}</p>
                    <div>
                        <h4>Email</h4>
                        <a href="mailto:${record.email}">${record.email}</a>
                    </div>
                </div>
            </div>

            <div id="blogger${loop.index}" class="collapse" aria-labelledby="headerBloggerName${loop.index}"
                 data-parent="#blogAccordion">
              <div class="card-body">
                % for post in record.posts:
                    <article>
                        <h2 class="collapse-trigger" id="blogger${loop.parent.index}article${loop.parent.index}Name">
                            <a data-toggle="collapse" data-target="#blogger${loop.parent.index}article${loop.index}" aria-expanded="true" aria-controls="blogger${loop.parent.index}article${loop.index}">
                                ${post.title}
                            </a>
                        </h2>
                        <span class="publish-date">${post.publish_date}</span>

                        <div class="collapse ${'show' if loop.index == 0 else ''}" id="blogger${loop.parent.index}article${loop.index}" aria-labelledby="blogger${loop.parent.index}article${loop.parent.index}Name">
                            ${post.rendered}
                        </div>

                    </article>
                % endfor
              </div>
            </div>
          </section>
    % endfor

</div>
</body>
</html>