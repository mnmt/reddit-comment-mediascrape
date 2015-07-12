import praw
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urlparse
import webbrowser
from bs4 import BeautifulSoup
import time
import os
import codecs

replace_comments = 0

print("Obtaining reddit instance...")
user_agent = "Desktop:anime_discussion_comments:v1.0.0 (by /u/PurposeDevoid)"
r = praw.Reddit(user_agent=user_agent)

print("Small anime subreddit scan")
anime = r.get_subreddit('anime')
anime_hot5 = list(anime.get_hot(limit=10))
anime_wiki = anime.get_wiki_page("discussion_archive/2015")
[print(x) for x in anime_hot5]
print("|+|"*18)
#print(anime_wiki.content_md)
#print("Last revised {} by {}".format(time.ctime(anime_wiki.revision_date),anime_wiki.revision_by.name))

## Get wiki page, links to episodes.
print("Beautiful soup on wiki.....")
sub_ids = []
soup = BeautifulSoup(anime_wiki.content_html, 'html.parser')
print("Soupified wiki page!")
for link in soup.find_all('a'):
    if link.text.lower() == "link":
        #print(link.get('href'))
        url_obj = urlparse(link.get('href'))
        netloc = url_obj.netloc # 'redd.it' or 'reddit.com'
        path = url_obj.path # e.g. gets '/2rza0f' or '/r/anime/comments/2rza0f/spoilers_rollinggirls_episode_1_discussion/'
        if netloc == "redd.it":
            sub_id = path.split('/')[1] # gets '2rza0f', second element (backslashes proudce extra empty elements)
        elif netloc == "reddit.com":
            sub_id = path.split('/')[4] # gets '2rza0f', fourth element
        else:
            print("Error, netloc should not be",netloc)
        sub_ids.append(sub_id)
print("Discussion ids obtained")

#episode = r.get_submission(submission_id = sub_ids[0])
episode = r.get_submission(submission_id = '2rza0f')

# Replaces episode.comments with version with full comments, replaces MoreComments
# Really slow, might be worth skipping? Default comments loaded are first 200 or so
print("There are", episode.num_comments,"comments, up to 200 loaded")
if replace_comments:
    print("Replacing 'MoreComments' instances with comments...")
    episode.replace_more_comments(limit=None, threshold=0)
else: # remove MoreComments
    print("Deleting all 'MoreComments' instances without replacing...")
    episode.replace_more_comments(limit=0, threshold=0)

print("Flattening comments for iteration...")
flat_comments = praw.helpers.flatten_tree(episode.comments)
sum_comments = "".join([comment.body_html for comment in flat_comments])

soup_com = BeautifulSoup(sum_comments, 'html.parser')
links = [(link.text,link.get('href')) for link in soup_com.find_all('a') if "http" == link.get('href')[:4]]

#print(sorted(links))

env = Environment(loader = FileSystemLoader(r'.\templates'))
template = env.get_template('gifs.jinja2')
ren = template.render(giflinks=links)

with codecs.open("gifs.html", "w", "utf-8-sig") as text_file: # http://stackoverflow.com/a/934203
    text_file.write(ren)
webbrowser.open('file://' + os.path.realpath("gifs.html"))

# https://www.reddit.com/r/anime/comments/2rza0f/spoilers_rollinggirls_episode_1_discussion/
# http://redd.it/2rza0f
