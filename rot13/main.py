# Copyright 2016 Google Inc.
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

import os
import webapp2
import jinja2
import re

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        self.render("main.html")

class Rot13(Handler):
    def convert_rot13(self, text):
        rot13 = ""
        if text:
            for char in text:
                if char.isalpha():
                    num_text = ord(char)
                    if char.islower():
                        if num_text >= 110:
                            num_text -= 26
                    if char.isupper():
                        if num_text >= 78:
                            num_text -= 26
                    rot13_num = num_text + 13
                    rot13 += str(unichr(rot13_num))
                else: 
                    rot13 += char
        return rot13

    def get(self):
        self.render("rot13.html")

    def post(self):
        input_text = self.request.get("text")
        rot13_text = input_text.encode('rot13')
        #self.convert_rot13(input_text)
        self.render("rot13.html", rot13_text = rot13_text)

class SignUp(Handler):
    
    def validate_user(self, username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return username and USER_RE.match(username)

    def validate_pass(self, password):
        PASS_RE = re.compile(r"^.{3,20}$")
        return password and PASS_RE.match(password)

    def verify_pass(self, password, verify):
        return password == verify

    def validate_email(self, email):
        EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
        return not email or EMAIL_RE.match(email)

    def get(self):
        self.render("signup.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        user_error = ""
        pass_error = ""
        verify_error = ""
        email_error = ""

        valid_user = self.validate_user(username)
        valid_pass = self.validate_pass(password)
        valid_verify = self.verify_pass(password, verify)
        valid_email = self.validate_email(email)

        if not valid_user:
            user_error = "That's not a valid username."
        if not valid_pass:
            pass_error = "That's not a valid password."
        else:
            if not valid_verify:
                verify_error = "Your passwords didn't match."
        if email:
            if not valid_email:
                email_error = "That's not a valid email."        

        if valid_user and valid_pass and valid_verify and valid_email:
            self.redirect("/welcome?username="+username)
        else:
            self.render("signup.html", username = username, email = email, user_error = user_error, pass_error = pass_error, verify_error = verify_error, email_error = email_error)

class SignUpHandler(Handler):
    def get(self):
        username = self.request.get("username")
        self.render("welcome.html", username = username)

app = webapp2.WSGIApplication([
    ('/', MainPage), ('/rot13', Rot13), ('/signup', SignUp), ('/welcome', SignUpHandler)
], debug=True)
