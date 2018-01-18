from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantMenu.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class WebserverHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'>"
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>Restaurants"
                restaurantes = session.query(Restaurant).all()

                for restaurant in restaurantes:
                     output += "<p>%s</p>" % restaurant.name
                     output += "<a href = '/restaurant/%s/update' >Update</a>" % restaurant.id
                     output += "<br>"
                     output += "<a href = '/restaurant/%s/delete' >Delete</a>" % restaurant.id
                     output += "<br>"
                     output += "<br>"
                output += "</br>"
                output += "</br>"
                output += "<a href = '/restaurants/new' >New Restaurante</a>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/items"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                output = ""
                output += "<html><body>Hello!"

                items = session.query(MenuItem).all()
                for item in items:
                    output += "<p>%s</p>" % item.name
                    output += "<p>%s</p>" % item.price
                    output += "<p>%s</p>" % item.restaurant.name
                    output += "<a href = '/update' >Update</a>"
                    output += "<br>"
                    output += "<a href = '/delete' >Delete</a>"
                    output += "</br>"
                    output += "<br>"
                    output += "<br>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/update"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(
                id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                
                    output = ""
                    output += "<html><body>Update!"
                    output += "<h1>Update Restaurant</h1>"
                    output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurant/%s/update'>" % restaurantIDPath
                    output += "<input name = 'newRestaurantName>' type = 'text' placeholder = '%s' > " % myRestaurantQuery.name
                    output += "<input type='submit' value='Rename'>"
                    output += "</form></body></html>"
                    self.wfile.write(output)
                

            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(
                id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    output = ""
                    output += "<html><body>Update!"
                    output += "<h1>Delete Restaurant %s</h1>" % myRestaurantQuery.name
                    output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurant/%s/delete'>" % restaurantIDPath
                    output += "<input type='submit' value='Delete'>"
                    output += "<Form></body></html>"
                    self.wfile.write(output)
                return
        except:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                    newRestaurant = Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/update"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurantIDPath = self.path.split("/")[2]
                    myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

                    if myRestaurantQuery != []:
                        myRestaurantQuery.name = messagecontent[0]
                        session.add(myRestaurantQuery)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()
           
            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurantIDPath = self.path.split("/")[2]
                    myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

                    session.delete(myRestaurantQuery)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
        except:
            pass
   

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()
        
    except KeyboardInterrupt:
        print "^C enterd, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()