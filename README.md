makesite.py
===========

Take full control of your personal fanfic archive generation by using this 
custom static site generator in
Python. That's right! We've reinvented the wheel!

[![View Source][SOURCE-BADGE]](makesite.py)
[![View Demo][DEMO-BADGE]](https://tmug.github.io/makesite-demo)
[![MIT License][LICENSE-BADGE]](LICENSE.md)

[SOURCE-BADGE]: https://img.shields.io/badge/view-source-brightgreen.svg
[DEMO-BADGE]: https://img.shields.io/badge/view-demo-brightgreen.svg
[LICENSE-BADGE]: https://img.shields.io/badge/license-MIT-blue.svg


Contents
--------

* [Introduction](#introduction)
* [To Do List](#to-do-list)
* [But Why?](#but-why)
* [Get Started](#get-started)
* [The Code](#the-code)
* [Layout](#layout)
* [Content](#content)
* [Configuration](#configuration)
* [FAQ](#faq)
* [Credits](#credits)
* [License](#license)
* [Support](#support)


Introduction
------------

This project borrows a lot of code and structure from the original 
makesite.py. However, it differs from that project's stated objectives in a 
few ways:
* You don't need to read the source code to proceed but you probably will 
need to read the documentation
* This project is designed to both be used as a fork OR used as-is and still 
be updated by the user from this repository. Thus the content directory is 
excluded from git, many configuration options are available, and theme 
directories are designed to be copied before being modified.

You are [free](LICENSE.md) to copy, use, and modify this project for
your website, so go ahead and fork this repository and make it
your own project. Change the [layout](layout) if you wish to, improve
the [stylesheet](static/css/style.css) to suit your taste, enhance
[makesite.py](makesite.py) if you need to, and develop your website/blog
just the way you want it.

To Do List
------------

This is a list of things that are required before the project will be ready for an alpha release.

### Code: 
* Create sample content, including fake AO3 works
* Finalise default themes, including dark/light theme switcher
* Test quick run shell script for OSX (Windows .cmd file is complete)
* Before Beta: JSON file output for use in frontend scripts
* Before Beta: RSS support
* Before Beta: Updated automated tests

### Documentation:
* Complete the Get Started section
* Document all configuration options and how to use them
* Code walkthrough (like the original makesite.py)
* Complete feature list
* Document advanced usage, like single directory output

Things not yet implemented that I would like to have by beta release:

Get Started
-----------

This section provides some quick steps to get you off the ground as
quickly as possible.

 1. It is highly recommended to run this program out of a python virtual 
environment to avoid the need to install additional packages.

    For a quick demo on your local system, just enter these commands:
 
    **Windows**: Run `makesite.cmd` by double-clicking on it.
    
    From a Command Window or Powershell, make sure the makesite directory is 
    the current working directory, e.g. by typing `cd path\to\makesite`. Then
    run:
    ```
    makesite.cmd
    python -m http.server -d _site
    ```
    
    Then visit http://localhost:8000/.
    
   
 2. 

        python makesite.py
        python -m http.server -d _site

    Note: In some environments, you may need to use `python3` instead of
    `python` to invoke Python 3.x.

 

    Note: Unlike the original makesite.py, this version only supports Python 
3.x

 3. For an Internet-facing website, you would be hosting the static
    website/blog on a hosting service and/or with a web server such as
    Apache HTTP Server, Nginx, etc. You probably only need to generate
    the static files and know where the static files are and move them
    to your hosting location.

    The `_site` directory contains the entire generated website. The
    content of this directory may be copied to your website hosting
    location.


The Code
--------

Now that you know how to generate the static website that comes with
this project, it is time to see what [makesite.py](makesite.py) does.
You probably don't really need to read the entire section. The source
code is pretty self-explanatory but just in case, you need a detailed
overview of what it does, here are the details:

 1. The `main()` function is the starting point of website generation.
    It calls the other functions necessary to get the website generation
    done.

 2. First it creates a fresh new `_site` directory from scratch. All
    files in the [static directory](static) are copied to this
    directory. Later the static website is generated and written to this
    directory.

 3. Then it creates a `params` dictionary with some default parameters.
    This dictionary is passed around to other functions. These other
    functions would pick values from this dictionary to populate
    placeholders in the layout template files.

    Let us take the `subtitle` parameter for example. It is set
    to our example website's fictitious brand name: "Lorem Ipsum". We
    want each page to include this brand name as a suffix in the title.
    For example, the [about page](https://tmug.github.io/makesite-demo/about/)
    has "About - Lorem Ipsum" in its title. Now take a look at the
    [page layout template](layout/page.html) that is used as the layout
    for all pages in the static website. This layout file uses the
    `{{ subtitle }}` syntax to denote that it is a placeholder that
    should be populated while rendering the template.

    Another interesting thing to note is that a content file can
    override these parameters by defining its own parameters in the
    content header. For example, take a look at the content file for
    the [home page](content/_index.html). In its content header, i.e.,
    the HTML comments at the top with key-value pairs, it defines a new
    parameter named `title` and overrides the `subtitle` parameter.

    We will discuss the syntax for placeholders and content headers
    later. It is quite simple.

 4. It then loads all the layout templates. There are 6 of them in this
    project.

      - [layout/page.html](layout/page.html): It contains the base
        template that applies to all pages. It begins with
        `<!DOCTYPE html>` and `<html>`, and ends with `</html>`. The
        `{{ content }}` placeholder in this template is replaced with
        the actual content of the page. For example, for the about page,
        the `{{ content }}` placeholder is replaced with the the entire
        content from [content/about.html](content/about.html). This is
        done with the `make_pages()` calls further down in the code.

      - [layout/post.html](layout/post.html): It contains the template
        for the blog posts. Note that it does not begin with `<!DOCTYPE
        html>` and does not contain the `<html>` and `</html>` tags.
        This is not a complete standalone template. This template
        defines only a small portion of the blog post pages that are
        specific to blog posts.  It contains the HTML code and the
        placeholders to display the title, publication date, and author
        of blog posts.

        This template must be combined with the
        [page layout template](layout/page.html) to create the final
        standalone template. To do so, we replace the `{{ content }}`
        placeholder in the [page layout template](layout/page.html) with
        the HTML code in the [post layout template](layout/post.html) to
        get a final standalone template. This is done with the
        `render()` calls further down in the code.

        The resulting standalone template still has a `{{ content }}`
        placeholder from the [post layout template](layout/post.html)
        template.  This `{{ content }}` placeholder is then replaced
        with the actual content from the [blog posts](content/blog).

      - [layout/list.html](layout/list.html): It contains the template
        for the blog listing page, the page that lists all the posts in
        a blog in reverse chronological order. This template does not do
        much except provide a title at the top and an RSS link at the
        bottom.  The `{{ content }}` placeholder is populated with the
        list of blog posts in reverse chronological order.

        Just like the [post layout template](layout/post.html) , this
        template must be combined with the
        [page layout template](layout/page.html) to arrive at the final
        standalone template.

      - [layout/item.html](layout/item.html): It contains the template
        for each blog post item in the blog listing page. The
        `make_list()` function renders each blog post item with this
        template and inserts them into the
        [list layout template](layout/list.html) to create the blog
        listing page.

      - [layout/feed.xml](layout/feed.xml): It contains the XML template
        for RSS feeds. The `{{ content }}` placeholder is populated with
        the list of feed items.

      - [layout/item.xml](layout/item.xml): It contains the XML template for
        each blog post item to be included in the RSS feed. The
        `make_list()` function renders each blog post item with this
        template and inserts them into the
        [layout/feed.xml](layout/feed.xml) template to create the
        complete RSS feed.

 5. After loading all the layout templates, it makes a `render()` call
    to combine the [post layout template](layout/post.html) with the
    [page layout template](layout/page.html) to form the final
    standalone post template.

    Similarly, it combines the [list layout template](layout/list.html)
    template with the [page layout template](layout/page.html) to form
    the final list template.

 6. Then it makes two `make_pages()` calls to render the home page and a
    couple of other site pages: the [contact page](content/contact.html)
    and the [about page](content/about.html).

 7. Then it makes two more `make_pages()` calls to render two blogs: one
    that is named simply [blog](content/blog) and another that is named
    [news](content/news).

    Note that the `make_pages()` call accepts three positional
    arguments:

      - Path to content source files provided as a glob pattern.
      - Output path template as a string.
      - Layout template code as a string.

    These three positional arguments are then followed by keyword
    arguments. These keyword arguments are used as template parameters
    in the output path template and the layout template to replace the
    placeholders with their corresponding values.

    As described in point 2 above, a content file can override these
    parameters in its content header.

 8. Then it makes two `make_list()` calls to render the blog listing
    pages for the two blogs. These calls are very similar to the
    `make_pages()` calls. There are only two things that are different
    about the `make_list()` calls:

      - There is no point in reading the same blog posts again that were
        read by `make_pages()`, so instead of passing the path to
        content source files, we feed a chronologically reverse-sorted
        index of blog posts returned by `make_pages()` to `make_list()`.
      - There is an additional argument to pass the
        [item layout template](layout/item.html) as a string.

 9. Finally it makes two more `make_list()` calls to generate the RSS
    feeds for the two blogs. There is nothing different about these
    calls than the previous ones except that we use the feed XML
    templates here to generate RSS feeds.

To recap quickly, we create a `_site` directory to write the static site
generated, define some default parameters, load all the layout
templates, and then call `make_pages()` to render pages and blog posts
with these templates, call `make_list()` to render blog listing pages
and RSS feeds. That's all!

Take a look at how the `make_pages()` and `make_list()` functions are
implemented. They are very simple with less than 20 lines of code each.
Once you are comfortable with this code, you can begin modifying it to
add more blogs or reduce them. For example, you probably don't need a
news blog, so you may delete the `make_pages()` and `make_list()` calls
for `'news'` along with its content at [content/news](content/news).


Layout/Theme
------

In this project, the layout template files are located in the [theme
directory](theme). Two themes are provided by default:
* Default
* Minimal

If you wish to modify the theme, I strongly recommend you make a copy of 
the theme you wish to modify. Just rename the folder to something descriptive
and change ["theme"]: "default" in params.json to use your new folder name.

## Templates 

Templates are made using Jinja2. There are 4 main templates used:
* **base.html.j2**: The layout for the header and footer for all pages
* **single.html.j2**: The layout for the content portion of a single page
* **list.html.j2**: The layout for a list of content, i.e. an index.html page
* **summary.html.j2**: The layout for each individual content item (e.g. 
work) 
in a list

You can override these for each folder in the content directory by creating a 
folder inside the templates directory. 

Content
-------

In this project, the content files are located in the [content
directory](content). Most of the content files are written in HTML.
However, the content files for the blog named [blog](content/blog) are
written in Markdown.

The notion of headers in the content files is supported by
[makesite.py](makesite.py). Each content file may begin with one or more
consecutive HTML comments that contain headers. Each header has the
following syntax:

    <!-- <key>: <value> -->

Any whitespace before, after, and around the `<!--`, `<key>`, `:`,
`<value>`, and `-->` tokens are ignored. Here are some example headers:

    <!-- title: About -->
    <!-- subtitle: Lorem Ipsum -->
    <!-- author: Admin -->

It looks for the headers at the top of every content file. As soon as
some non-header text is encountered, the rest of the content from that
point is not checked for headers.

By default, placeholders in content files are not populated during
rendering. This behaviour is chosen so that you can write content freely
without having to worry about makesite interfering with the content,
i.e., you can write something like `{{ title }}` in the content and
makesite would leave it intact by default.

However if you do want to populate the placeholders in a content file,
you need to specify a parameter named `render` with value of `yes`. This
can be done in two ways:

  - Specify the parameter in a header in the content file in the
    following manner:

        <!-- render: yes -->

  - Specify the parameter as a keyword argument in `make_pages` call.
    For example:

        blog_posts = make_pages('content/blog/*.md',
                                '_site/blog/{{ slug }}/index.html',
                                post_layout, blog='blog', render='yes',
                                **params)

Configuration
-------------

Configuration is handled in the params.json file (this is what the original 
makesite.py called it). This file will be created from defaults the first 
time the program is run.

There are a number of options available to you. The options for processing 
AO3 files are in the "config" option.
Where an array (list) of options is requested, the list of lists will also 
be surrounded by square brackets and comma-separated, and it will have a 
trailing comma (because it is part of the larger "config" parameter. 

**base_path**: URL fragment be prepended to all links generated within the site. 
e.g. if your site is located in the 'works' subfolder of your site, enter `"base_path": "/works/",`

**render**: Perform text replacement inside the content files. Change this to anything else to disable this feature. Default is "yes".

**site_title**: Used by the theme as the main title for the site

**subtitle**: Used by the theme as the secondary title for the site.

**author**: Default author for all pages/works in the site

**theme**: Which theme (see Themes) to use. Default: "default"

**pretty_uris**: Do the page URLs look like `https://example.com/works/Title of Work/` or `https://example.com/works/Title of Work.html`. Default: true

**flatten_site_structure**: Output all content in a single directory. Subfolders in the 'content' folder will be used to group pages in the final, singular index.html file. See below for more details.

**include_folders_in_index**: The link to each subfolders and any metadata in _index.html will be included in the index.html file for each folder. 

**header_menu**: Used by the theme to generate a top menu for the site. Sample: "header_menu": [ { "uri": "/works", "text": "Works" },  { "uri": "/news", "text": "News" },  { "uri": "/blog", "text": "Blog" } ],

**footer_menu**: Used by the theme to generate a footer menu for the site. Sample: "header_menu": [  { "uri": "https://twitter.com/", "text": "Twitter" }, { "uri": "https://tumblr.com/", "text": "Tumblr"}, { "uri": "https://dreamwidth.org/", "text": "Dreamwidth" } ],

**Order by**: Define the sorting order of pages in a list. Each sort field 
is given as an array with the sort field and a boolean (true/false) to 
define whether it will be in descending order.
`"order_by": [["fandom", false],["date", true],["title", false]],`

**Group by**: In a page list, items will be grouped by these fields in 
order. Please note that where a page has multiple values for a field, e.g. 
if it is in multiple fandoms, the page metadata will be repeated for each 
group. If you are using fandom groups (see below), include "subfandom" if 
you want the secondary fandoms to be included in the list.
`"group_by": [ "fandom", "subfandom", "series"],`
      
**Fandom navigation** Used by the included themes to determine whether or 
not to display a list of all fandoms at the top of the page. Please note 
that if fandom groups are enabled this will only include the top level 
(group) fandoms in the list.
`"fandom_nav": true,`

**Merge tags**: Option to merge fandoms into one, e.g. put all MCU fandoms 
in one bucket, merge LotR the book and LotR the movie into one fandom. This 
will <em>replace</em> the tags in the list with one tag. You can also use 
this to rename tags, for example if you wanted your works to be rated 
"Lemon" instead of "Explicit."
How to enable: In the params.json file, add a new set of tags to 
'merge_tags', in array format (i.e. surrounded by square brackets, comma 
separated. Each item should be surrounded by double quotes.) The first tag 
is the one that all subsequent items will be merged into. 
e.g. I want to merge all "Captain America (Movies)" and "Captain America 
(Comics)" into one single "Captain America" fandom. My "merge_tags" setting 
will now look like this:
`"merge_tags": [ ["Captain America", "Captain America (Movies)", "Captain 
America (Comics)"] ],`
I also want to merge "全职高手 - 蝴蝶蓝 | Quánzhí Gāoshǒu - Húdié Lán" and 
"全职高手 | The King's Avatar (Live Action TV)" to just "The King's Avatar". 
My "merge_tags" parameter will now look like this:
`"merge_tags": [ ["Captain America", "Captain America (Movies)", "Captain 
America (Comics)"], [ "The King's Avatar", "全职高手 - 蝴蝶蓝 | Quánzhí 
Gāoshǒu - Húdié Lán", "全职高手 | The King's Avatar (Live Action TV)"] ],`

**Fandom Groups**: When grouping the works list by Fandom, this provides the 
option to group certain fandoms into one bucket.
How to use: Each grouping should be an array. Put the top-level fandom as 
the first item in the array, followed by the fandoms to be grouped 
underneath it. The top level fandom will now be the "fandom" 
`"fandom_groups": [ [ "Marvel Cinematic Universe", "Avengers (2012)", "The 
Avengers (Marvel Movies)", "Agent Carter (TV)", "Captain America (Movies)" ] 
]`

**Exclude tags**: Option to completely ignore certain tags. This tag will 
not be available to use in templates or to filter or group works.
How to enable: In params.json, under "Config", add your tags to the 
"excluded_tags" parameter array.
e.g. `"excluded_tags": [ "Angst", "Found Family" ],`

**Ignore series:** When grouping by series or in work metadata, ignore this 
series - useful e.g. if you have set up a "My MCU works" series
 
**Media tags:** Identify which freeform tags you have that define the medium 
of the work (fanfiction, fanart, fanvid, etc). You can then use this in 
templates or enter 'media_type' in the group_by configuration to group by 
this in the works list. Use the `media_type_default` option to define what 
media type should be used when no tag is available on the work.
How to use: 
```
"media_tags": ["fanfiction", "fanart", "fanvid"],
"media_type_default": "fanfiction",
```


FAQ
---

Here are some frequently asked questions along with answers to them:

 1. Can you add feature X to this project?

    I do not have any plans to add new features to this project. It is
    intended to be as minimal and as simple as reasonably possible. This
    project is meant to be a quick-starter-kit for developers who want
    to develop their own static site generators. Someone who needs more
    features is free to fork this project repository and customize the
    project as per their needs in their own fork.

 2. Can you add support for Jinja templates, YAML front matter, etc.?

    I will not add or accept support for Jinja templates, YAML front
    matter, etc. in this project. However, you can do so in your fork.
    The reasons are explained in the first point.

 3. Do you accept any new features from the contributors?

    I do not accept any new features in this project. The reasons are
    explained in the first point.

 4. Do you accept bug fixes and improvements?

    Yes, I accept bug fixes and minor improvements that do not increase
    the scope and complexity of this project.

 5. Are there any contribution guidelines?

    Yes, please see [CONTRIBUTING.md](CONTRIBUTING.md).

 6. How do I add my own copyright notice to the source code without
    violating the terms of license while customizing this project in my
    own fork?

    This project is released under the terms of the MIT license. One of
    the terms of the license is that the original copyright notice and
    the license text must be preserved. However, at the same time, when
    you edit and customize this project in your own fork, you hold the
    copyright to your changes. To fulfill both conditions, please add
    your own copyright notice above the original copyright notice and
    clarify that your software is a derivative of the original.

    Here is an example of such a notice where a person named J. Doe
    wants to reserve all rights to their changes:

        # Copyright (c) 2018-2019 J. Doe
        # All rights reserved

        # This software is a derivative of the original makesite.py.
        # The license text of the original makesite.py is included below.

    Anything similar to the above notice or something to this effect is
    sufficient.


Credits
-------

Thanks to:

  - [Susam Pal](https://github.com/susam) for the initial documentation
    and the initial unit tests.
  - [Keith Gaughan](https://github.com/kgaughan) for an improved
    single-pass rendering of templates.


License
-------

This is free and open source software. You can use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of it,
under the terms of the [MIT License](LICENSE.md).

This software is provided "AS IS", WITHOUT WARRANTY OF ANY KIND,
express or implied. See the [MIT License](LICENSE.md) for details.


Support
-------

To report bugs, suggest improvements, or ask questions, please visit
<https://github.com/sunainapai/makesite/issues>.
