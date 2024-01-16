makesite.py
===========

This program takes a folder of fanfic in html form, and creates the html files for a personal fanfic archive with an index and working links between all the fic. 

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

This project is based on the Python custom static site generator makesite.py, but is designed to be useable without a coding background.  

It can be used in two ways:

* For non-coders: Run the code as a program, using the provided customisation tools. If you download an updated version of this project in the future, it won't override your fanfic or customisation.  
* For coders who want extra customisation: Create your own new fork of the code. You are [free](LICENSE.md) to copy, use, and modify this project, specifically the [layout](layout) and [stylesheet](static/css/style.css).

Some of the text of this README was taken from the README for [ao3downloader](https://github.com/nianeyna/ao3downloader). 

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

### Install *makesite*
1. Install [python](https://www.python.org/downloads/). Make sure to install version 3.0 or later. 
2. Download this project's repository as a zip file by clicking on the "Code" button and selecting "Download ZIP". The "repository" is the folder containing the code. 
3. Unzip the zip file you just downloaded. Open the new *makesite* folder this creates. 

### Run the *makesite* script
This updates the archive files, and while it's running the script will create a local version of your archive only visible on your computer.

1. Run the *makesite* script from inside the *makesite* folder. The method depends on your operating system:
   - Windows: double-click on `makesite.cmd`.
   - Mac: Run `makesite.sh` from a terminal window pointed to the *makesite* folder: 
        - Right click on the *makesite* directory, choose "Services" and then "New Terminal at folder" from the menu. Alternatively, you can type "cd " and drag the folder to the terminal to copy the folder path.
        - In the terminal window, type: ```sh makesite.sh```. Wait until text stops scrolling down the screen. 
2. Open http://localhost:8000/ in a web browser to see a temporary local preview version of your archive. This will remain visible on your computer while the *makesite* script is running. If you haven't added any content yet, you should see the default *makesite* home page. 
3. When you're done, stop the *makesite* script:
    - windows: ??
    - mac: Type Control-C in the terminal window.  

### Update the content of your archive

The first time you run the *makesite* script it will create a *makesite/content* directory with some sample files. 

After that, any time you run the *makesite* script, it will go through the files in the *makesite/content* directory and use them to create the html files for your archive in the *makesite/_site* folder. 

To change your archive, edit or add to the files in the *makesite/content* directory and run the *makesite* script again. You can check out the effect of your changes at http://localhost:8000/ while the script is running. 

See below for documentation on how to make specific changes and add fanfic to your archive.

If you want to download a large number of works from the AO3, check out [ao3downloader](https://github.com/nianeyna/ao3downloader). 

### Upload your archive to the internet

First, make sure you're happy with how your archive looks by running the *makesite* script and checking out the local copy of your archive at http://localhost:8000/. 

The html files for your achive are in the *makesite/_site* folder. Upload the contents of this folder to a website host like [neocities](https://neocities.org/). 

Whenever you want to update your archive, edit the files in the *makesite/content* directory and run the *makesite* script again. Then upload the updated contents of the *makesite/_site* folder to your web host, over-writing the older files with the updated versions. 
    
Theme
------

If you are happy with the appearance of the archive, you can skip this section.
 
The appearance and layout of the archive are controlled by the theme. The theme is defined by files within a subfolder of the [theme directory](theme).   

Two themes are provided by default:
* modular: a customisable theme which applies different settings to different parts of the archive.
* minimal: A simple theme which applies the same settings to all pages. 

To change the theme, change the line ```["theme"]: "modular"``` in *params.json*, eg if you wish to use the modular theme, change the line to ```["theme"]: "minimal"```.

## Creating your own theme

First, create a copy of whichever default theme is closest to what you want, and rename the folder to something descriptive, like *my_theme*. Then change the relevant line of *params.json* eg to ```["theme"]: "my_theme"```.

Each theme folder has two relevant subfolders: 
  - css: CSS files defining the colours and fonts.
  - templates: Jinja2 files defining the layout, structure and label text. 

### CSS

The two files in the css folder are style.css, which defines the light theme, and style-dark.css, which defines the dark theme. 

If you're not familiar with CSS, there are many tutorials online. 

### Templates 

Templates are made using Jinja2, which is a templating language combining python and html. There are 4 main templates used:
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
