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

def read_ao3_content(content, text, **params):
    from bs4 import BeautifulSoup
    config = params.get("config")
    soup = BeautifulSoup(text, 'html.parser')
    # log(soup.prettify())
    content['title']= soup.h1.get_text()
    authors = soup.find_all('a', rel="author")
    authors = map(lambda author: author.get_text(), authors)
    content['author'] = ', '.join(list(authors))
    meta = soup.find('div', class_="meta")
    # log(meta)
    tags = meta.find('dl', class_="tags")
    if ( summary_label := soup.find('p', text='Summary') ):
        content['summary'] = summary_label.find_next('blockquote', class_="userstuff").decode_contents(formatter='minimal')
    if ( notes_label := soup.find('p', text='Notes') ):
        content['notes'] = notes_label.find_next('blockquote', class_="userstuff").decode_contents(formatter='minimal')
    if ( end_notes_label := soup.find('p', text='End Notes')):
        content['end_notes'] = end_notes_label.find_next('blockquote', class_="userstuff").decode_contents(formatter='minimal')
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

    if "media_tags" in config and not content.get("media_type"):
        content["media_type"] = config.get("media_type_default")

    matches = re.findall(r"^\s*(Words|Chapters|Published): ([0-9,.\--/]*)", content['Stats'], re.MULTILINE)
    if matches:
        for label, value in matches:
            content.update({ label: value })
    content["date"] = content.pop("Published")
    # text = soup.find(id='chapters', class_="userstuff").decode_contents(formatter='minimal')
    text = soup.body.decode_contents(formatter='minimal')
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
            content = { k.casefold().replace(' ', '_'): v for k, v in content.items() }
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

def render(template, **params):
    # Replace placeholders in template with values from params.
    return re.sub(r'{{\s*([^}\s]+)\s*}}',
                  lambda match: str(params.get(match.group(1).casefold(),match.group(0))),
                  template)

def render_metadata(params, template):
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
        # Populate placeholders in content if content-rendering is enabled.
        if page_params.get('render') == 'yes':
            rendered_content = render(page_params['content'], **render_metadata(page_params, template='single') )
            page_params['content'] = rendered_content
            content['content'] = rendered_content

        items.append(content)

        dst_path = render(dst, **page_params)
        output = render(layout, **page_params)

        log('Rendering {} => {} ...', src_path, dst_path)
        fwrite(dst_path, output)

    return items
    # return sorted(items, key=lambda x: x['date'], reverse=True)


def make_list(posts, dst, list_layout, item_layout, **params):
    """Generate list page for a blog."""
    config = params.get("config")
    items = []
    if params.get('type') == params.get("config").get("works_folder"):

        posts.sort(key=sort_works, reverse=False)
        curr_fandom = None
        fandom_works = {}
        current_series = None
        for post in posts:
            item_params = dict(params, **post)
            item = render(item_layout, **render_metadata(item_params, template="summary"))
            fandoms = post.get('fandom')
            if post.get('series'):
                for series in post.get('series'):
                    if current_series != series.get('title'):
                        item = f'<h3>{series.get("title")}</h3>' + item
                        current_series = series.get('title')
            for fandom in fandoms:
                if fandom_works.get(fandom):
                    fandom_works[fandom].append(item)
                else:
                    fandom_works[fandom] = [item]
        if config.get('fandom_groups'):
            for fandom_grouping in config.get('fandom_groups'):
                for fandom in fandom_grouping:
                    fandom_group = fandom_grouping[0]
                    works = fandom_works.pop(fandom, False)
                    if (works):
                        if not fandom_works.get(fandom_group):
                            fandom_works[fandom_group] = []
                        fandom_works[fandom_group] += [f'<h2 class="subheading">{fandom}</h2>']
                        fandom_works[fandom_group] += works
        for fandom, works in sorted(fandom_works.items()):
            items.append(f'<h2>{fandom}</h2>')
            items += works
    else:
        posts.sort(key=lambda x: x['date'], reverse=True)
        for post in posts:
            item_params = dict(params, **post)
            item_params['summary'] = truncate(post['content'])
            item = render(item_layout, **item_params)
            items.append(item)

    params['content'] = ''.join(items)
    dst_path = render(dst, **params)
    output = render(list_layout, **params)

    log('Rendering list => {} ...', dst_path)
    fwrite(dst_path, output)

def sort_works(key):
    if key.get('series'):
        series_sort = []
        for item in key.get('series'):
            series_sort.extend([item.get('title'), int((item.get('index') ))])
        return tuple(series_sort)
    else:
        return ( key.get('date'), "0" )

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
        shutil.rmtree('_site')
    shutil.copytree(f'{ theme_dir }/static', '_site')

    # If params.json exists, load it.
    if os.path.isfile('params.json'):
        params.update(json.loads(fread('params.json')))

    # Load layouts.\
    page_layout = fread(f'{ theme_dir }/templates/base.html')
    single_layout = fread(f'{ theme_dir }/templates/single.html')
    list_layout = fread(f'{ theme_dir }/templates/list.html')
    summary_layout = fread(f'{ theme_dir }/templates/summary.html')
    feed_xml = fread(f'{ theme_dir }/templates/feed.xml')
    item_xml = fread(f'{ theme_dir }/templates/item.xml')

    # Combine layouts to form final layouts.
    single_layout = render(page_layout, content=single_layout, **params)
    list_layout = render(page_layout, content=list_layout, **params)

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
        if os.path.isfile(f'{ theme_dir }/templates/{folder}/single.html'):
            folder_single_layout = fread(f'{ theme_dir }/templates/{folder}/single.html')
            folder_single_layout = render(page_layout, content=folder_single_layout, **params)
        folder_items = make_pages(f'content/{folder}/[!_]*.*',
                                f'_site/{folder}/{{{{ slug }}}}/index.html',
                                folder_single_layout, type=folder, **folder_params)

        folder_summary_layout = summary_layout
        if os.path.isfile(f'{ theme_dir }/templates/{folder}/summary.html'):
            folder_summary_layout = fread(f'{ theme_dir }/templates/{folder}/summary.html')

        make_list(folder_items, f'_site/{folder}/index.html',
                  list_layout, folder_summary_layout, type=folder, path=folder, title=folder.title(), **folder_params)

        # # Create RSS feeds.
        # make_list(blog_posts, '_site/blog/rss.xml',
        #           feed_xml, item_xml, type='blog', title='Blog', **params)
        # make_list(news_posts, '_site/news/rss.xml',
        #           feed_xml, item_xml, type='news', title='News', **params)

# Test parameter to be set temporarily by unit tests.
_test = None


if __name__ == '__main__':
    main()
