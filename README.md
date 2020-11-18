# Blogchecker

This python script automates the job of monitoring student blogs. A per-blog summary report notifies lecturers of the total number of posts, and the date of last post for each student. Reports are colour-coded to instantly highlight potential issues. All blog content is federated into a single file to allow content to be read quickly and for the purposes of record keeping.

![Screenshot showing blog report interface](https://s3-eu-west-1.amazonaws.com/jackoneill.assethosting/BlogCheckerScreenshot.png)

## Creating Wordpress Blogs
This script works with the [Wordpress REST API](https://developer.wordpress.org/rest-api/) to scrape the content of all blogs. Because of this, blogs must be created on Wordpress and have their visibility set to **public**. See the [wordpress website](https://wordpress.com) for a guide on how to create a new blog (it's very quick and straightforward). Blog privacy settings can be managed from the dashboard (Settings -> Privacy -> Public)

## Usage
[Install Python 3.X](https://www.python.org/downloads/) if you haven't already. Download this repoistory and from a terminal run

```bash
pip install -r requirements.txt
```

to install the required dependencies. Create a new file called *BlogList.csv* (you can use the sample as a template) and fill in the information as required. When you're run the script using

```bash
python -m blogchecker.py
```

When complete, the script will generate a html file in the current directory containing all of the students' blog content as well as summary information on each student. Open this file in your favourite browser


### Command-line Options
Use the --help flag to retrieve a list of command-line options

```bash
python blogchecker.py --help
```

## Contributing
Contributions and pull requests are always welcome. Please use the Issues to report any issues or make any feature requests. This project grew from a personal script for a very particular use-case but I'm happy to generalise it and built out features if there's a demand.

