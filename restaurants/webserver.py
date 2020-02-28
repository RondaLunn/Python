from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Restaurant, Base, MenuItem
 
engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)

session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>Hello!"
                output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
                output += "</body></html>"

                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>&#161Hola! <a href='/hello'>Back to Hello</a>"
                output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
                output += "</body></html>"

                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = session.query(Restaurant).all()
                
                output = ""
                output += "<html><body><h1>Restaurants</h1>"
                output += "<a href='/restaurants/new'>Make a New Restaurant</a>"

                output += "<ul>"

                for restaurant in restaurants:
                    output += "<li> %s </br>" % restaurant.name
                    output += "<a href='/restaurants/%s/edit'>Edit</a></br><a href='/restaurants/%s/delete'>Delete</a>" % (restaurant.id, restaurant.id)
                    output += "</li></br>"
                
                output += "</ul>"

                output += "</body></html>"

                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
              
                output = ""
                output += "<html><body><h1>Make a New Restaurant</h1>"
                output += "<a href='/restaurants'>Back to Restaurants</a>"

                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><input name='restaurant' type='text'><input type='submit' value='Create'></form>"

                output += "</body></html>"

                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                id_number = self.path.split('/')[2]

                restaurant = session.query(Restaurant).filter_by(id = id_number).one()

                output = ""
                output += "<html><body><h1>%s</h1>" % restaurant.name
                output += "<a href='/restaurants'>Back to Restaurants</a>"

                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'><input name='restaurant' type='text' placeholder='%s'><input type='submit' value='Rename'></form>" % (restaurant.id, restaurant.name)

                output += "</body></html>"

                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                id_number = self.path.split('/')[2]

                restaurant = session.query(Restaurant).filter_by(id = id_number).one()

                output = ""
                output += "<html><body><h1>Are you sure you want to delete %s?</h1>" % restaurant.name
                output += "<a href='/restaurants'>Back to Restaurants</a>"

                output += "<form method='POST' action='/restaurants/%s/delete'><input type='submit' value='Delete'></form>" % restaurant.id

                output += "</body></html>"

                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)
    
    def do_POST(self):
        if self.path.endswith("/restaurants/new"):
            try:

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurant')

                restaurant = Restaurant(name = messagecontent[0])
                session.add(restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            except:
                pass
        
        if self.path.endswith("/edit"):
            try:
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurant')

                id_number = self.path.split('/')[2]
                restaurant = session.query(Restaurant).filter_by(id = id_number).one()

                restaurant.name = messagecontent[0]
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            except:
                pass

        if self.path.endswith("/delete"):
            try:
                id_number = self.path.split('/')[2]
                restaurant = session.query(Restaurant).filter_by(id = id_number).one()

                session.delete(restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            except:
                pass

        else:
            try:
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                output = ""
                output += "<html><body>"
                output += "<h2> Okay, how about this: </h2>"
                output += "<h1> %s </h1>" % messagecontent[0]

                output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
                output += "</body></html>"

                self.wfile.write(output)
                print output

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

            except:
                pass


def main() :
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()