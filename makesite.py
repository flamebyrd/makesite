#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2018-2022 Sunaina Pai
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""Make static website/blog with Python."""


import os
import shutil
import re
import glob
import sys
import json
import datetime
import jinja2
import copy
from itertools import groupby
from collections.abc import Iterable
from collections import defaultdict
import pathlib
import urllib


def fread(filename):
    """Read file and close the file."""
    with open(filename, 'r', encoding="utf-8") as f:
        return f.read()


def fwrite(filename, text):
    """Write content to file and close the file."""
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)

    with open(filename, 'w', encoding="utf-8") as f:
        f.write(text)


def log(msg, *args):
    """Log message with specified arguments."""
    sys.stderr.write(msg.format(*args) + '\n')


def truncate(text, words=25):
    """Remove tags and truncate text to the specified number of words."""
    return ' '.join(re.sub('(?s)<.*?>', ' ', text).split()[:words])


def read_headers(text):
    """Parse headers in text and yield (key, value) tuples."""
    for match in re.finditer(r'\s*<!--\s*(.+?)\s*:\s*(.+?)\s*-->\s*|.+', text):
        if not match.group(1):
            break
        yield match.group(1), match.group(2), match.end()


def rfc_2822_format(date_str):
    """Convert yyyy-mm-dd date string to RFC 2822 format date string."""
    d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return d.strftime('%a, %d %b %Y %H:%M:%S +0000')

def read_content(filename, **params):
    """Read content and metadata from file into a dictionary."""

    log("Reading: " + filename)

    # Read file content.
    text = fread(filename)

    # Read metadata and save it in a dictionary.
    date_slug = os.path.basename(filename).split('.')[0]
    match = re.search(r'^(?:(\d\d\d\d-\d\d-\d\d)-)?(.+)$', date_slug)
    content = {
        'date': match.group(1),
        'slug': match.group(2),
    }

    if new_space := params.get("replace_spaces_in_filename_with", False):
        content['slug'] = content['slug'].replace(' ', new_space)
    
    if filename.endswith(('.html')) and '<div id="preface">' in text:
        # File is probably an AO3 work
        try:
            if _test == 'ImportError':
                raise ImportError('Error forced by test')
            ao3_content, text = read_ao3_content(text, **params)
            content.update(**ao3_content)
            content["content_type"] = params.get('ao3_content_type', 'ao3_work')
        except ImportError as e:
            log('WARNING: Cannot read HTML in {}: {}', filename, str(e))
    else:
        # Read headers.
        end = 0
        for key, val, end in read_headers(text):
            content[key] = val

        # Separate content from headers.
        text = text[end:]

        if not content.get('content_type') and not params.get('content_type'):
            content['content_type'] = params.get('default_content_type', 'page')

        # Convert Markdown content to HTML.
        if filename.endswith(('.md', '.mkd', '.mkdn', '.mdown', '.markdown')):
            try:
                if _test == 'ImportError':
                    raise ImportError('Error forced by test')
                import commonmark
                text = commonmark.commonmark(text)
            except ImportError as e:
                log('WARNING: Cannot render Markdown in {}: {}', filename, str(e))

    from datetime import date

    # Update the dictionary with content and RFC 2822 date.
    content['content'] = text
    if ( content.get('date') ):
        content.update({
            'rfc_2822_date': rfc_2822_format(content['date']),
            'date_obj': date.fromisoformat(content['date'])
        })

    return content

def read_ao3_content(text, **params):
    from bs4 import BeautifulSoup
    config = params.get("tag_processing")
    content = {}
    # soup = BeautifulSoup(text, 'html.parser')
    soup = BeautifulSoup(text, "lxml")
    content['title']= soup.h1.get_text()
    preface = soup.find('div', id='preface')
    meta = preface.find('div', class_="meta")
    tags = meta.find('dl', class_="tags")
    afterword = soup.find('div', id='afterword')
    authors = preface.find('div', class_="byline").find_all('a', rel="author")
    content['author'] = list(map(lambda author: author.get_text(), authors))
    if ( summary_label := preface.find('p', string='Summary') ):
        content['summary'] = summary_label.find_next('blockquote', class_="userstuff").decode_contents(formatter='minimal')
    if ( notes_label := preface.find('p', string='Notes') ):
        content['notes'] = notes_label.find_next('blockquote', class_="userstuff").decode_contents(formatter='minimal')
    if ( end_notes_label := afterword.find('p', string='End Notes')):
        content['end_notes'] = end_notes_label.find_next('blockquote', class_="userstuff").decode_contents(formatter='minimal')
    if ( top_message := preface.find('p', class_="message") ):
        content['top_message'] = top_message.decode_contents(formatter='minimal')
    if ( bottom_message := afterword.find('p', class_="message") ):
        content['bottom_message'] = bottom_message.decode_contents(formatter='minimal')
    for tag in tags.find_all('dt'):
        tag_name = tag.get_text().rstrip(':').casefold()
        tag_val = tag.find_next("dd").find_all('a')
        if (tag_val):
            if "series" == tag_name:
                series = []
                for link in tag_val:
                    series_index = re.search(r'\d+', link.find_previous_sibling(string=True)) or 0
                    if series_index:
                        series_index = series_index.group()
                    series_title = link.get_text().strip()
                    if not series_title in config.get("exclude_series", []):
                        series.append({ "index": series_index, "title": series_title })
                tag_val = series
            elif "additional tags" == tag_name:
                filtered_tags = []
                media_tags = config.get("media_tags", [])
                excluded_tags = config.get("excluded_tags", [])
                excluded_tags = [x.casefold() for x in excluded_tags]
                for freeform_tag in tag_val:
                    tag_text = freeform_tag.get_text()
                    try: # Use the version of the media tag in the params for formatting
                        media_tag_index = [x.casefold() for x in media_tags].index(tag_text.casefold())
                        media_tag = media_tags[media_tag_index]
                        if content.get("media_type"):
                            content["media_type"].append(media_tag)
                        else:
                            content["media_type"] = [ media_tag ]
                    except ValueError:                        
                        if not tag_text.casefold() in excluded_tags:
                            filtered_tags.append(tag_text)
                tag_val = filtered_tags
            else:
                tag_val = list(map(lambda val: val.get_text(), tag_val))
        else:
            tag_val = tag.find_next("dd").get_text()
        if isinstance(tag_val, list):
            tag_val = merge_tags(tag_val, config.get("merge_tags", []))
        if merge_fieldnames := params.get("merge_fieldnames", False):
            if tag_name in merge_fieldnames.keys():
                tag_name = merge_fieldnames[tag_name]
        content[tag_name] = tag_val

    for fields in afterword.find_all('dt'):
        field_name = tag.get_text().rstrip(':')
        field_val = tag.find_next("dd").find_all('a')
        if (field_val):
            if "Works inspired by this one" == field_name:
                content["related_works"] = tag_val
            else:
                content[tag_name] = tag_val

    if "media_tags" in config and not content.get("media_type"):
        content["media_type"] = config.get("media_type_default")

    matches = re.findall(r"^\s*(Words|Chapters|Published): ([0-9,.\--/]*)", content['stats'], re.MULTILINE)
    if matches:
        for label, value in matches:
            content.update({ label: value })

    content["date"] = content.pop("Published")

    # Make all keys lowercase
    content = { k.casefold().replace(' ', '_').replace('\'"', ''): v for k, v in content.items() }

    if "words" in content:
        import locale
        locale.setlocale(locale.LC_ALL, '')
        content['words'] = locale.atoi(content['words'])
    chapters_div = soup.find(id='chapters', class_="userstuff")
    text = chapters_div.decode_contents(formatter='minimal')
    chapters = []
    current_chapter = {}
    for div in chapters_div.find_all('div', recursive=False):
        css_class = div.get("class")
        if "meta" in css_class:
            if chapter_title := div.find('h2', class_="heading"):
                if current_chapter: #If we find a chapter heading we should add the previous chapter to the list
                    chapters.append(current_chapter)
                    current_chapter = {}
                current_chapter["title"] = chapter_title.get_text()
            if chapter_summary_label := div.find('p', string="Chapter Summary"):
                current_chapter["summary"] = chapter_summary_label.find_next_sibling('blockquote', class_="userstuff").decode_contents(formatter='minimal')
            if chapter_notes_label := div.find('p', string="Chapter Notes"):
                chapter_notes_content = chapter_notes_label.find_next_sibling('blockquote', class_="userstuff") 
                if chapter_notes_content: #If the chapter only had an end note the script was grabbing the end notes here
                    current_chapter["notes"] = chapter_notes_content.decode_contents(formatter='minimal')
            if chapter_end_notes_label := div.find('p', string="Chapter End Notes"):
                current_chapter["end_notes"] = chapter_end_notes_label.find_next_sibling('blockquote', class_="userstuff").decode_contents(formatter='minimal')
        elif "userstuff" in css_class:
                current_chapter["content"] = div.decode_contents(formatter='minimal')
        else:
            continue
    if current_chapter: #Make sure last  chapter is added
        chapters.append(current_chapter)   
    content["chapters_content"] = list(chapters) 
    soup.decompose()

    return content, text

def merge_tags( tags, merge_list ):
    output_tags = []
    for tag in tags:
        merged = False
        for merge in merge_list:
            merge_to = merge[0]
            if tag in merge:
                merged = True
                if not merge_to in output_tags:
                    output_tags.append(merge_to)
        if not merged:
            output_tags.append(tag)
    return output_tags

def render(template, **params):
    # Replace placeholders in template with values from params.
    return re.sub(r'{{\s*([^}\s]+)\s*}}',
                  lambda match: str(params.get(match.group(1).casefold(),match.group(0))),
                  template)

# Formats a number as 1K, 2.5K, 1M, etc. From https://stackoverflow.com/a/45478574
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def render_metadata(params, template):
    # This function is not currently being used, but retained for posterity
    config = params.get('config')
    formatters = config.get('custom_formatters')
    formatter_defaults = { 'key': None, 'format': "{}", 'wrapper': None, 'separator': ', ', 'template': 'all'}
    metadata_defaults = { 'series': '' }
    active_formatters = {}
    for formatter in formatters:
        formatter = { **formatter_defaults, **formatter }
        if formatter.get('template') not in (template, 'all'): continue
        key = formatter.get('key')
        if not key: continue
        active_formatters[key] = formatter
    for key, param in params.items():
        formatter = active_formatters.get(key)
        format = None
        separator = formatter_defaults.get('separator')
        if formatter:
            format = formatter.get('format')
            separator = formatter.get('separator')
        if isinstance(param, list):
            if format:
                param = [format_metadata(p, format) for p in param]
            else:
                param = [str(p) for p in param]
            params[key] =  separator.join(param)
        elif isinstance(param, str):
            if format:
                params[key] =  format.format(param)
        if formatter and (wrapper := formatter.get('wrapper')):
            params[key] = wrapper.format(params[key])
    return { **metadata_defaults, **params }

def format_metadata(val, format):
    return format.format(**val)

def flatten_by_attribute(value, attribute):
    output = []
    for item in value:
        if properties := item.get(attribute):
            if 'series' == attribute:
                for property in properties:
                    output.append({ **item, **{'series': property.get('title'), 'series_index': property.get('index') } })
            elif not isinstance(properties, str) and isinstance(properties, Iterable):
                for property in properties:
                    output.append({ **item, **{attribute: property} })
            else:
                output.append(item)

        else:
            output.append({ **item, **{attribute: ''} })
    return output

def group_fandoms(config, works):
    fandom_groups = config.get('fandom_groups', [])
    if not fandom_groups: return works
    grouped_works = []
    for work in works:
        if fandoms := work.get('fandom'):
            for fandom in fandoms:
                grouped = False
                for fandom_grouping in fandom_groups:
                    fandom_group = fandom_grouping[0]
                    if fandom in fandom_grouping:
                        grouped_works.append({ **work, **{'fandom': fandom_group, 'subfandom': fandom} })
                        grouped = True
                if not grouped:
                    grouped_works.append({ **work, **{'fandom': fandom} })

        else:
            grouped_works.append({ **work, **{'fandom': config.get('no_fandom_label','')} })
    return grouped_works

def group_recursive(items, groups, depth = 0):
    output = []
    attribute = groups[depth]
    items = flatten_by_attribute(items, attribute) # If the attribute is a list this will fix it
    items.sort(key=lambda x: x.get(attribute)) # groupby() requires input to be sorted
    for group, values in groupby(items, key=lambda x: x.get(attribute)):
        values = list(values)
        if depth+1 < len(groups):
            group_items = []
            empty_group = False
            next_group = group_recursive(values, groups, depth+1) # To understand recursion you must first understand recursion
            if (group): # Only adding it to the output if the group has a value
                # FB: Disabled until I figure out a better solution for this issue
                # for i, item in enumerate(next_group): #Checking the next iteration to see if contains an empty group
                #     if not item[0]:
                #         empty_group = i
                #         group_items = item[1] #Add the empty group's items to this group
                #         break
                # if empty_group: #Remove the empty group
                #     next_group.pop(empty_group)
                output.append((group, group_items, depth))
            output.extend(next_group)
        else:
            # This will output an empty group - it would be better if we could append it
            #  to the previous non-empty group instead so the depth is useful in the template
            output.append((group, values, depth))
    return output

def generate_uri(content):
    site_dir = os.path.normpath(content.get('output_dir', '_site'))
    if content.get('dst_path'):
        # match = re.search(f'^{site_dir}/(.*?)/index.html$', content['dst_path'])
        # uri = re.sub(f'^{site_dir}{re.escape(os.sep)}', f'{content.get("base_path")}/', content['dst_path'])
        uri = os.path.relpath(content['dst_path'], site_dir)
        uri = uri.replace('\\', '/')
        uri = urllib.parse.urljoin(content.get("base_path"), uri)
        uri = re.sub('/index.html$', '', uri)
        return uri
    return f"{content['base_path']}/{content['slug']}"

def generate_html_id(text):
    text = text.replace(" ", "_")
    text = text.casefold()
    return re.sub("\W", "", text)

def make_pages(src, dst, layout, **params):
    """Generate pages from page content."""
    items = []
    series_nav = defaultdict(dict)

    for src_path in glob.glob(src):
        content = read_content(src_path, **params)
        content = dict(params, **content)

        content['src_path'] = src_path

        # If the file is index.html we don't want to create a subfolder for it
        if os.path.basename(src_path) == 'index.html':
            content['slug'] = ''          
            content['dst_path'] = render(dst, **content ).replace('//', '/')
        else:
            content['dst_path'] = render(dst, **content)

        if not content.get('uri'):
            content['uri'] = generate_uri(content)

        #Put all series information in a list so we can generate next/previous work links
        if series := content.get('series'):
            for s in series:
                series_nav[s.get('title')][s.get('index')] = { 'uri': generate_uri(content), 'title': content['title'] }

        items.append(content)

    #Create the content files, and generate series navigation
    for content in items:
        if series := content.get('series'):
            for i, s in enumerate(series):
                series_works = series_nav.get(s.get('title'))
                current_index = int(s.get('index'))
                if next_work := series_works.get(str(current_index +1)):
                    s['next'] = next_work
                if prev_work := series_works.get(str(current_index -1)):
                    s['prev'] = prev_work

        # page_params = dict(params, **content)

        # This functionality is disabled until I figure out what to do with keyword replacement in content files
        # Populate placeholders in content if content-rendering is enabled.
        # if page_params.get('render') == 'yes':
            # # rendered_content = render(page_params['content'], **render_metadata(page_params, template='single') )
            # rendered_content = render(**render_metadata(page_params, template='single'))
            # page_params['content'] = rendered_content
            # content['content'] = rendered_content

        # page_params = render_metadata(page_params, template='single')

        # rel_path = os.path.relpath(content['src_path'], 'content')

        output = layout.render(**content)
        
        import hashlib
        contents_hash = hashlib.md5(output.encode())
        content['md5'] = contents_hash.hexdigest()

        if not content.get('skip_rendering'):
            log('Rendering {} => {} ...', content['src_path'], content['dst_path'])
            fwrite(content['dst_path'], output)

    return items
    # return sorted(items, key=lambda x: x['date'], reverse=True)

def make_list(files, dst, list_layout, item_layout, **params):
    """Generate list page for a blog."""
    config = params.get("display_options")
    items = []

    #Python sort is stable and it's generally recommended to sort multiple times if needed
    if order_by := config.get("order_by"):
        if isinstance(order_by[0], str):
            files.sort(key=lambda x: x.get(order_by[0]) or '', reverse=order_by[1])
        else:
            for attr, rev in reversed(order_by):
                files.sort(key=lambda x: x.get(attr) or '', reverse=rev)
    else:
        files.sort(key=lambda x: x.get("date") or '', reverse=True)

    if config.get("group_by") and "series" in config.get("group_by"):
        files.sort(key=sort_series, reverse=True)
    
    for item in files:
        item_params = dict(params, **item)
        if not item_params.get('summary'):
            item_params['summary'] = truncate(item['content'])
        if item_layout:
            item_content = item_layout.render(**item_params)
            # item_params = render_metadata(item_params, template="summary")
            item_params['content'] = item_content
        if not item_params.get('exclude_from_index', False): 
            items.append(item_params)
    
    if (config.get('group_by')):
        items = group_fandoms(params.get("tag_processing"), items)

    params['items'] = items
    if (dst):
        dst_path = render(dst, **params)
        params["dst_path"] = dst_path
        params["uri"] = generate_uri(params)
        log('Rendering list => {} ...', dst_path)
        output = list_layout.render(**params)
        fwrite(dst_path, output)
    else:
        output = list_layout.render(**params)
    
    return output

def sort_series(item):
    if item.get('series'):
        series_sort = []
        for series in item.get('series'):
            series_sort.extend([series.get('title'), -(int((series.get('index')) ))])
        return tuple(series_sort)
    else:
        return ( '', 0 )

def get_templates(template_env, theme_dir, folder):
    single_layout = template_env.get_template('single.html.j2')
    list_layout = template_env.get_template('list.html.j2')
    summary_layout = template_env.get_template('summary.html.j2')
    needed_templates = { 'single': True, 'summary': True, 'list': True}
    folder_tree = folder.split(os.sep)
    theme_templates_dir = os.path.join(theme_dir, 'templates')
    while folder_tree:
        template_path = os.path.join(*folder_tree)
        print('Template path: ' + template_path)
        if os.path.isdir(os.path.join(theme_templates_dir, template_path)):
            template_filenames = os.listdir(os.path.join(theme_templates_dir, template_path))
            if needed_templates['single'] and 'single.html.j2' in template_filenames:
                single_layout = template_env.get_template( pathlib.posixpath.join(template_path, 'single.html.j2'))
                needed_templates['single'] = False
            if needed_templates['summary'] and 'summary.html.j2' in template_filenames:
                summary_layout = template_env.get_template( pathlib.posixpath.join(template_path, 'summary.html.j2'))
                needed_templates['summary'] = False
            if needed_templates['list'] and 'list.html.j2' in template_filenames:
                list_layout = template_env.get_template( pathlib.posixpath.join(template_path, 'list.html.j2'))
                needed_templates['list'] = False
        folder_tree.pop()
    return (single_layout, list_layout, summary_layout)

def main():

    # Default parameters.
    params = {
        'base_path': '/',
        'render': 'yes',
        "site_title": "My Fanfic Site",
        'subtitle': 'Site Sub Title',
        'author': 'Sample Author',
        'theme': 'default',
        'current_year': datetime.datetime.now().year,
        'pretty_uris': True,
        "flatten_site_structure": False,
        "include_folders_in_index": False,
        "ao3_content_type": "ao3_work", 
        "replace_spaces_in_filename_with": False,
        'display_options': {
            "//order_by": [["fandom", False],["date", True],["title", False]],
            "order_by": ["date", True],
            "group_by": [ "fandom", "subfandom", "series"],
            "group_nav": True,
            "fandom_nav": True,
            "series_prefix": "Series: ",
            "display_copyright": True
         },
        'tag_processing': {
            "media_tags": ["fanfiction", "fanart", "fanvid", "podfic"],
            "media_type_default": "fanfiction",
            "excluded_tags": [],
            "merge_tags": [],
            "fandom_groups": [],
         },
         'merge_fieldnames': {
            'fandoms': 'fandom',
            'relationships': 'relationship',
            'characters': 'character',
            'categories': 'category',
            'additional tag': 'additional_tags',
            'archive warnings': 'archive_warning'
         }
    }

    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

    # If params.json exists, load it, otherwise create it.
    if os.path.isfile('params.json'):
        # We can't do a traditional merge because this dictionary contains another dictionary
        user_params = json.loads(fread('params.json'))
        # params.update(user_params)
        for key, val in  user_params.items():
            if params.get(key) and isinstance(val, dict):
                params[key].update(val)
            else:
                params[key] = val
    else:
        # Adding some additional default parameters for new projects
        params["header_menu"] = [
            {
              "uri": "/about",
              "text": "About"
            },
            {
              "uri": "/contact",
              "text": "Contact"
            }
        ]
        params["footer_menu"] = [
            {
              "uri": "https://twitter.com/",
              "text": "Twitter"
            },
            {
              "uri": "https://tumblr.com/",
              "text": "Tumblr"
            },
            {
              "uri": "https://dreamwidth.org/",
              "text": "Dreamwidth"
            }
        ]
        with open('params.json', 'w') as outfile:
            json.dump(params, outfile, indent=2)

    theme_dir = f"themes/{params.get('theme', 'default') }"
    site_dir = params.get('output_dir', '_site')

    # Create a new _site directory from scratch.
    if os.path.isdir(site_dir):
        shutil.rmtree(site_dir, ignore_errors=False)
    shutil.copytree(f'{ theme_dir }/static', site_dir)

    #Load Jinja2 templates
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(f'{ theme_dir }/templates'))
    template_env.trim_blocks = True
    template_env.lstrip_blocks = True
    template_env.filters["flattenbyattribute"] = flatten_by_attribute
    template_env.filters["grouprecursive"] = group_recursive
    template_env.filters["htmlid"] = generate_html_id
    template_env.filters["humanformat"] = human_format

    single_layout = template_env.get_template('single.html.j2')
    list_layout = template_env.get_template('list.html.j2')
    summary_layout = template_env.get_template('summary.html.j2')

    # Create subfolder pages.
    theme_folder_templates = False
    # if os.listdir(os.path.join(theme_dir, 'templates')):
    if next(os.walk(os.path.join(theme_dir, 'templates')))[1]:
        theme_folder_templates = True

    site_output = list() #Only used if site structure is flattened

    if not os.path.isdir('content'):
        shutil.copytree(f'sample-content/default', 'content')

    for (dirpath, dirnames, filenames) in os.walk('content', topdown=True):
        log('Reading ' + dirpath)
        dirnames.sort()
        folder_params = copy.deepcopy(params)
        folder = os.path.relpath(dirpath, 'content')
        folder_items = list()

        # Fetching metadata for the index page (also sets defaults for content in this folder)
        if os.path.isfile( os.path.join(dirpath, '_index.html') ):
            folder_params.update(read_content(os.path.join(dirpath, '_index.html'), **folder_params))
        elif os.path.isfile( os.path.join(dirpath, '_index.md') ):
            folder_params.update(read_content(os.path.join(dirpath, '_index.md'), **folder_params))
            
        if params.get('include_folders_in_index'):
            for dirname in dirnames:
                if os.path.isfile( os.path.join(dirpath, dirname, '_index.html') ):
                    folder_content = read_content( os.path.join(dirpath, dirname, '_index.html'), **params)
                elif os.path.isfile( os.path.join(dirpath, dirname, '_index.md') ):
                    folder_content = read_content( os.path.join(dirpath, dirname, '_index.md'), **params)
                if folder_content:
                    dst_path = os.path.join(site_dir, folder, dirname, 'index.html')          
                    folder_content['uri'] = generate_uri( { 'base_path': params['base_path'], 'dst_path': dst_path })                    
                    folder_items.append(folder_content)
                
        # Fetch content templates from theme, starting in the current folder and walking back up the folder tree
        # This allows overriding templates with ones from closer in the file tree
        if theme_folder_templates: 
            single_layout, list_layout, summary_layout = get_templates(template_env, theme_dir, folder)

        if params.get('pretty_uris'):
            dst_path = os.path.normpath(os.path.join(site_dir, folder, '{{ slug }}/index.html'))
        else:
            dst_path = os.path.normpath(os.path.join(site_dir, folder, '{{ slug }}.html'))
            
        folder_items += make_pages(os.path.join(dirpath, '[!_]*.*'), dst_path, single_layout, **folder_params)

        if not os.path.isfile(os.path.join(dirpath, 'index.html')):
            if params.get('flatten_site_structure'):
                folder_params['content'] = make_list(folder_items, None, list_layout, summary_layout, standalone=True, **folder_params)
                log('Adding ' + dirpath)
                site_output.append(folder_params)
            else:
                make_list(folder_items, os.path.normpath(os.path.join(site_dir, folder, 'index.html')),
                list_layout, summary_layout, **folder_params)

        # # Create RSS feeds.
        # make_list(blog_posts, '_site/blog/rss.xml',
        #           feed_xml, item_xml, type='blog', title='Blog', **params)
        # make_list(news_posts, '_site/news/rss.xml',
        #           feed_xml, item_xml, type='news', title='News', **params)
    if params.get('flatten_site_structure'):
        make_list(site_output, os.path.normpath(os.path.join(site_dir, 'index.html')), list_layout, item_layout = False, **params)

# Test parameter to be set temporarily by unit tests.
_test = None


if __name__ == '__main__':
    main()
