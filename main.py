#/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = (os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t= jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title   = db.StringProperty(required = True)
    body    = db.TextProperty(required   = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def get(self):
        self.redirect('/blog')

class FrontpageHandler(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post order by created desc limit 5")
        self.render('frontpage.html', posts=posts)

class ViewPostHandler(Handler):
    def get(self,id):
        post = Post.get_by_id(int(id))
        self.render('post.html', post = post)

class Newpost(Handler):
    def get(self):
        self.render('newpost.html')

    def post(self):
        title = self.request.get("title")
        body  = self.request.get("body")

        if title and body:
            a = Post(title=title,body=body)
            a.put()
            self.redirect('/blog/{}'.format(a.key().id()))
        else:
            self.render('newpost.html', title = title, body=body, error="We need both a title and a body!")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog/newpost', Newpost),
    ('/blog', FrontpageHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)
