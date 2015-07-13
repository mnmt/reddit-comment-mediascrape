import praw
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urlparse
import webbrowser
from bs4 import BeautifulSoup
import time
import os
import codecs
from collections import OrderedDict

replace_comments = 0

def submission_comments_scrape(submission):
    # Replaces submission.comments with version with full comments, replaces MoreComments
    # Really slow, might be worth skipping? Default comments loaded are first 200 or so
    print("There are", submission.num_comments,"comments, up to 200 loaded")
    if replace_comments:
        print("Replacing 'MoreComments' instances with comments...")
        submission.replace_more_comments(limit=None, threshold=0)
    else: # remove MoreComments
        print("Deleting all 'MoreComments' instances without replacing...")
        submission.replace_more_comments(limit=0, threshold=0)

    print("Flattening comments for iteration...")
    flat_comments = praw.helpers.flatten_tree(submission.comments)
    sum_comments = "".join([comment.body_html for comment in flat_comments])

    soup_com = BeautifulSoup(sum_comments, 'html.parser')
    links = [(link.text+" ({})".format(urlparse(link.get('href')).netloc),link.get('href')) for link in soup_com.find_all('a') if "http" == link.get('href')[:4]]
    return links

print("Obtaining Reddit instance...")
user_agent = "Desktop:anime_discussion_comments:v1.0.0 (by /u/PurposeDevoid)"
r = praw.Reddit(user_agent=user_agent)


print("Small anime subreddit scan")
anime = r.get_subreddit('anime')
anime_hot5 = list(anime.get_hot(limit=10))
[print(x) for x in anime_hot5]
print("|+|"*18)



## Get wiki page, links to episodes.
anime_wiki = anime.get_wiki_page("discussion_archive/2015") # https://www.reddit.com/r/anime/wiki/discussion_archive/2015
#print(anime_wiki.content_md)
print("Wiki Page Last revised {} by {}".format(time.ctime(anime_wiki.revision_date),anime_wiki.revision_by.name))
print("Applying Beautiful soup on wiki page.....")
sub_ids = []
soup = BeautifulSoup(anime_wiki.content_html, 'html.parser')
print("Soupified wiki page!")
for link in soup.find_all('a'):
    if link.text.lower() == "link":
        #print(link.get('href'))
        url_obj = urlparse(link.get('href')) # seems to normally be in "redd.it" format
        netloc = url_obj.netloc # 'redd.it' or 'reddit.com'
        path = url_obj.path # e.g.  '/2rza0f' or '/r/anime/comments/2rza0f/spoilers_rollinggirls_episode_1_discussion/'
        if netloc == "redd.it":
            sub_id = path.split('/')[1] # gets '2rza0f', second element (backslashes proudce extra empty elements)
        elif netloc == "reddit.com":
            sub_id = path.split('/')[4] # gets '2rza0f', fourth element
        else:
            print("Error, netloc should not be",netloc)
        sub_ids.append(sub_id)
print("Discussion ids obtained")

eps_dict = OrderedDict([])

#episode = r.get_submission(submission_id = sub_id)
episode = r.get_submission(submission_id = '2rza0f')
links = submission_comments_scrape(episode)
eps_dict[episode.title]=links

env = Environment(loader = FileSystemLoader(r'.\templates'))
template = env.get_template('gifs.jinja2')
ren = template.render(eps=eps_dict)

with codecs.open("gifs.html", "w", "utf-8-sig") as text_file: # http://stackoverflow.com/a/934203
    text_file.write(ren)
webbrowser.open('file://' + os.path.realpath("gifs.html"))



# https://www.reddit.com/r/anime/comments/2rza0f/spoilers_rollinggirls_episode_1_discussion/
# http://redd.it/2rza0f
