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
from itertools import groupby
from collections.abc import Iterable


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
    """Parse headers in text and yield (key, value, end-index) tuples."""
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

    log(filename)

    # Read file content.
    text = fread(filename)

    # Read metadata and save it in a dictionary.
    date_slug = os.path.basename(filename).split('.')[0]
    match = re.search(r'^(?:(\d\d\d\d-\d\d-\d\d)-)?(.+)$', date_slug)
    content = {
        'date': match.group(1) or '1970-01-01',
        'slug': match.group(2),
    }

    if filename.endswith(('.html')) and '<div id="preface">' in text:
        # File is probably an AO3 work
        log('Work: ' + filename)
        try:
            if _test == 'ImportError':
                raise ImportError('Error forced by test')
            content, text = read_ao3_content(content, text, **params)
            content = { k.casefold().replace(' ', '_').replace('\'"', ''): v for k, v in content.items() }
        except ImportError as e:
            log('WARNING: Cannot render Markdown in {}: {}', filename, str(e))
    else:
        # Read headers.
        end = 0
        for key, val, end in read_headers(text):
            content[key] = val

        # Separate content from headers.
        text = text[end:]

        # Convert Markdown content to HTML.
        if filename.endswith(('.md', '.mkd', '.mkdn', '.mdown', '.markdown')):
            try:
                if _test == 'ImportError':
                    raise ImportError('Error forced by test')
                import commonmark
                text = commonmark.commonmark(text)
            except ImportError as e:
                log('WARNING: Cannot render Markdown in {}: {}', filename, str(e))

    # Update the dictionary with content and RFC 2822 date.
    content.update({
        'content': text,
        'rfc_2822_date': rfc_2822_format(content['date'])
    })

    return content

def read_ao3_content(content, text, **params):
    from bs4 import BeautifulSoup
    config = params.get("config")
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
        tag_name = tag.get_text().rstrip(':')
        tag_val = tag.find_next("dd").find_all('a')
        if (tag_val):
            if "Series" == tag_name:
                series = []
                for link in tag_val:
                    series_index = re.search(r'\d+', link.find_previous_sibling(string=True)) or 0
                    if series_index:
                        series_index = series_index.group()
                    series.append({ "index": series_index, "title": link.get_text() })
                tag_val = series
            elif "Additional Tags" == tag_name:
                # if "media_tags" in params or "excluded_tags" in params:
                filtered_tags = []
                for freeform_tag in tag_val:
                    tag_text = freeform_tag.get_text()
                    if tag_text in config.get("media_tags", []):
                        if content.get("media_type"):
                            content["media_type"].append(tag_text)
                        else:
                            content["media_type"] = [ tag_text ]
                    elif not tag_text in config.get("excluded_tags", []):
                        filtered_tags.append(tag_text)
                tag_val = filtered_tags
            else:
                tag_val = list(map(lambda val: val.get_text(), tag_val))
        else:
            tag_val = tag.find_next("dd").get_text()
        if isinstance(tag_val, list):
            tag_val = merge_tags(tag_val, config.get("merge_tags", []))
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

    matches = re.findall(r"^\s*(Words|Chapters|Published): ([0-9,.\--/]*)", content['Stats'], re.MULTILINE)
    if matches:
        for label, value in matches:
            content.update({ label: value })
    content["date"] = content.pop("Published")
    chapters_div = soup.find(id='chapters', class_="userstuff")
    text = chapters_div.decode_contents(formatter='minimal')
    chapters = []
    current_chapter = {}
    for div in chapters_div.find_all('div', recursive=False):
        if chapter_title := div.find('h2', class_="heading"):
            if current_chapter:
                chapters.append(current_chapter)
            current_chapter = {}
            current_chapter["title"] = chapter_title.get_text()
            if chapter_notes_label := div.find('p', string="Chapter Notes"):
                current_chapter["notes"] = chapter_notes_label.find_next('blockquote', class_="userstuff").decode_contents(formatter='minimal')
            elif chapter_notes_label := div.find('p', string="Chapter Summary"):
                current_chapter["summary"] = chapter_notes_label.find_next('blockquote', class_="userstuff").decode_contents(formatter='minimal')
        elif css_class := div.get("class"):
            if "userstuff" in css_class:
                current_chapter["content"] = div.decode_contents(formatter='minimal')
        elif chapter_end_notes_label := div.find('p', string="Chapter End Notes"):
            current_chapter["end_notes"] = chapter_end_notes_label.find_next('blockquote', class_="userstuff").decode_contents(formatter='minimal')
        else:
            continue
    content["chapters_content"] = list(chapters)
    #text = soup.body.decode_contents(formatter='minimal')
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

def make_pages(src, dst, layout, **params):
    """Generate pages from page content."""
    items = []

    for src_path in glob.glob(src):
        content = read_content(src_path, **params)

        page_params = dict(params, **content)
        # This section is disabled until I figure out what to do with keyword replacement in content files
        # Populate placeholders in content if content-rendering is enabled.
        # if page_params.get('render') == 'yes':
            # # rendered_content = render(page_params['content'], **render_metadata(page_params, template='single') )
            # rendered_content = render(**render_metadata(page_params, template='single'))
            # page_params['content'] = rendered_content
            # content['content'] = rendered_content

        # page_params = render_metadata(page_params, template='single')

        items.append(content)

        dst_path = render(dst, **page_params)

        output = layout.render(**page_params)

        log('Rendering {} => {} ...', src_path, dst_path)
        fwrite(dst_path, output)

    return items
    # return sorted(items, key=lambda x: x['date'], reverse=True)

def flattenbyattribute(value, attribute):
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
            grouped_works.append({ **work, **{'fandom': config.get('no_fandom_label','No Fandom')} })
    return grouped_works

def group_recursive(items, groups, depth = 0):
    output = []
    attribute = groups[depth]
    items = flattenbyattribute(items, attribute) # If the attribute is a list this will fix it
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

def make_list(files, dst, list_layout, item_layout, **params):
    """Generate list page for a blog."""
    config = params.get("config")
    items = []

    #Python sort is stable and it's generally recommended to sort multiple times if needed
    if order_by := config.get("order_by"):
        if isinstance(order_by[0], str):
            files.sort(key=lambda x: x.get(order_by[0]), reverse=order_by[1])
        else:
            for attr, rev in reversed(order_by):
                files.sort(key=lambda x: x.get(attr, 0), reverse=rev)
    else:
        files.sort(key=lambda x: x.get("date"), reverse=True)

    if "series" in config.get("group_by"):
        files.sort(key=sort_series, reverse=True)
    
    for item in files:
        item_params = dict(params, **item)
        if not item_params.get('summary'):
            item_params['summary'] = truncate(item['content'])
        item_content = item_layout.render(**item_params)
        # item_params = render_metadata(item_params, template="summary")
        item_params['content'] = item_content
        items.append(item_params)
    
    if (config.get('group_by')) and (fandom_groups := config.get('fandom_groups')):
        items = group_fandoms(config, items)

    # params['content'] = ''.join(items)
    params['items'] = items
    dst_path = render(dst, **params)
    output = list_layout.render(**params)

    log('Rendering list => {} ...', dst_path)
    fwrite(dst_path, output)

def sort_series(item):
    if item.get('series'):
        series_sort = []
        for series in item.get('series'):
            series_sort.extend([series.get('title'), -(int((series.get('index')) ))])
        return tuple(series_sort)
    else:
        return ( '', 0 )

def main():

    # Default parameters.
    params = {
        'base_path': '',
        'render': 'yes',
        'subtitle': 'Site Title',
        'author': 'Author',
        'site_url': 'http://localhost:8000',
        'theme': 'default',
        'current_year': datetime.datetime.now().year,
        'config': { }
    }

    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

    theme_dir = f"themes/{params.get('theme', 'default') }"

    # Create a new _site directory from scratch.
    if os.path.isdir('_site'):
        shutil.rmtree('_site', ignore_errors=False)
    shutil.copytree(f'{ theme_dir }/static', '_site')

    # If params.json exists, load it.
    if os.path.isfile('params.json'):
        params.update(json.loads(fread('params.json')))

    #Load Jinja2 templates
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(f'{ theme_dir }/templates'))
    template_env.filters["flattenbyattribute"] = flattenbyattribute
    template_env.filters["grouprecursive"] = group_recursive

    page_layout = template_env.get_template('single.html.j2')
    single_layout = template_env.get_template('single.html.j2')
    list_layout = template_env.get_template('list.html.j2')
    summary_layout = template_env.get_template('summary.html.j2')

    # Create site pages.
    make_pages('content/_index.html', '_site/index.html',
               page_layout, **params)
    make_pages('content/[!_]*.html', '_site/{{ slug }}/index.html',
               page_layout, **params)

    # Create subfolder pages.
    # Grab the list of top-level subfolders from the 'content' folder (next grabs first item of os.walk object, [1] grabs the second item in the returned tuple)
    content_folders = next(os.walk('content'))[1]
    params["folder_links"] = ' '.join( list( map( lambda folder: f"<a href=\"{ params.get('base_path') }/{ folder }\">{ folder.title() }</a>", content_folders ) ) )
    for folder in content_folders:
        folder_params = params
        if os.path.isfile(f'{folder}/_index.html'):
            folder_params.update(read_headers(fread(f'{folder}/_index.html')))

        folder_single_layout = single_layout
        log(f'{ theme_dir }/templates/{folder}/single.html.j2')
        if os.path.isfile(f'{ theme_dir }/templates/{folder}/single.html.j2'):
            folder_single_layout = template_env.get_template(f'{folder}/single.html.j2')
        folder_items = make_pages(f'content/{folder}/[!_]*.*',
                                f'_site/{folder}/{{{{ slug }}}}/index.html',
                                folder_single_layout, type=folder, **folder_params)

        folder_summary_layout = summary_layout
        if os.path.isfile(f'{ theme_dir }/templates/{folder}/summary.html.j2'):
            folder_summary_layout = template_env.get_template(f'{folder}/summary.html.j2')
        folder_list_layout = list_layout
        if os.path.isfile(f'{ theme_dir }/templates/{folder}/list.html.j2'):
            folder_list_layout = template_env.get_template(f'{folder}/list.html.j2')

        make_list(folder_items, f'_site/{folder}/index.html',
                  folder_list_layout, folder_summary_layout, type=folder, path=folder, title=folder.title(), **folder_params)

        # # Create RSS feeds.
        # make_list(blog_posts, '_site/blog/rss.xml',
        #           feed_xml, item_xml, type='blog', title='Blog', **params)
        # make_list(news_posts, '_site/news/rss.xml',
        #           feed_xml, item_xml, type='news', title='News', **params)

# Test parameter to be set temporarily by unit tests.
_test = None


if __name__ == '__main__':
    main()
