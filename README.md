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


Get Started
-----------

This section provides some quick steps to get you off the ground as
quickly as possible.

 1. It is highly recommended to run this program out of a python virtual 
environment to avoid the need to install additional packages. Note: Unlike the original makesite.py, this version only supports Python 3.x.

    For a quick demo on your local system, just enter these commands:
 
    **Windows**: Run `makesite.cmd` by double-clicking on it.
    
    From a Command Window or Powershell, make sure the makesite directory is 
    the current working directory, e.g. by typing `cd path\to\makesite`. Then
    run:
    ```
    makesite.cmd
    ```
    
    Then visit http://localhost:8000/.

    **MacOS**: Run `makesite.sh` in the code directory. Note: This file assumes that Python has been installed on MacOS with the name `python3`, not `python`. 

    e.g. From the directory above where you downloaded the makesite code, right click on the *makesite* directory, choose "services" and then "New Terminal at folder" from the menu.
    In the terminal window, type:
    ```
    sh makesite.sh
    ```

    Then visit http://localhost:8000/ 

 2. Copy your content into the `content` directory. You can use the same commands as in step 1 to re-rerun the program and see what changes.

 3. Make any configuration changes you want by modifying params.json (see below). Run the commands in step 1 again to see what changes.

 4. For an Internet-facing website, you would be hosting the static
    website/blog on a hosting service and/or with a web server such as
    Apache HTTP Server, Nginx, etc. You probably only need to generate
    the static files and know where the static files are and move them
    to your hosting location.

    The `_site` directory contains the entire generated website. The
    content of this directory may be copied to your website hosting
    location.
    

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

**display_options**: { (The following tags are in the display_options subsection)

**order_by**: Define the sorting order of pages in a list. Each sort field 
is given as an array with the sort field and a boolean (true/false) to 
define whether it will be in descending order.
`"order_by": [["fandom", false],["date", true],["title", false]],`

**group_by**: In a page list, items will be grouped by these fields in 
order. Please note that where a page has multiple values for a field, e.g. 
if it is in multiple fandoms, the page metadata will be repeated for each 
group. If you are using fandom groups (see below), include "subfandom" if 
you want the secondary fandoms to be included in the list.
`"group_by": [ "fandom", "subfandom", "series"],`

**group_nav**: When enabled, will display a clickable menu of the group headings at the top of the list. `"group_nav": true,`
      
**fandom_nav** Used by the included themes to determine whether or 
not to display a list of all fandoms at the top of the page. Please note 
that if fandom groups are enabled this will only include the top level 
(group) fandoms in the list.
`"fandom_nav": true,`

} (end of display_options)

**tag_processing**: { (The following options are in the tag_processing subsection)

**media_tags:** Identify which freeform tags you have that define the medium 
of the work (fanfiction, fanart, fanvid, etc). You can then use this in 
templates or enter 'media_type' in the group_by configuration to group by 
this in the works list. Use the `media_type_default` option to define what 
media type should be used when no tag is available on the work.
How to use: 
```
"media_tags": ["fanfiction", "fanart", "fanvid"],
"media_type_default": "fanfiction",
```

**excluded_tags**: Option to completely ignore certain tags. This tag will 
not be available to use in templates or to filter or group works.
How to enable: In params.json, under "Config", add your tags to the 
"excluded_tags" parameter array.
e.g. `"excluded_tags": [ "Angst", "Found Family" ],`

**merge_tags**: Option to merge fandoms into one, e.g. put all MCU fandoms 
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

**fandom_groups**: When grouping the works list by Fandom, this provides the 
option to group certain fandoms into one bucket.
How to use: Each grouping should be an array. Put the top-level fandom as 
the first item in the array, followed by the fandoms to be grouped 
underneath it. The top level fandom will now be the "fandom" 
`"fandom_groups": [ [ "Marvel Cinematic Universe", "Avengers (2012)", "The 
Avengers (Marvel Movies)", "Agent Carter (TV)", "Captain America (Movies)" ] 
]`

**exclude_series:** When grouping by series or in work metadata, ignore this 
series - useful e.g. if you have set up a "My MCU works" series.
 

FAQ
---

TO DO

 4. Do you accept bug fixes and improvements?

    Yes, I accept bug fixes and minor improvements.
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
