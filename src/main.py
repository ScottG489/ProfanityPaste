#from google.appengine.ext import webapp2
#from google.appengine.ext.webapp2.util import run_wsgi_app
import webapp2
import logging
import os
import jinja2
import cgi
from profanity_filter import ProfanitiesFilter

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader = jinja2.FileSystemLoader(TEMPLATE_DIR))

class PageHandler(webapp2.RequestHandler):
    def write_template(self, template_file, **params):
        template = JINJA_ENV.get_template(template_file)
        self.response.out.write(template.render(params))

    def write(self, string):
        self.response.out.write(string)

class MainPage(PageHandler):
    def get(self):
        logging.info('Handling GET request')
        self.response.headers['Content-Type'] = 'text/html'

        self.write_template('main_page.html')

    def post(self):
        logging.info('Handling POST request')


    def get_inputs(self):
        inputs = {}
        args = self.request.arguments()
        logging.info('Getting request inputs from args: ' + str(args))
        for name in args:
            value = self.request.get_all(name)
            if name != 'days':
                inputs[name] = value[0]
            else:
                inputs[name] = value

        return inputs

    def get_input_errors(self, inputs):
        logging.info('Getting user input errors if any')
        errors = {}
        if not inputs.get('start'):
            errors['start_error'] = 'Required field'
        if not inputs.get('end'):
            errors['end_error'] = 'Required field'
        if not inputs.get('days'):
            errors['days_error'] = 'Must select at least 1 day'
        if not self.is_valid_time(inputs.get('hour'), inputs.get('minute')):
            errors['time_error'] = 'Invalid time'

        return errors


class ContentHandler(PageHandler):
        def get(self):
            logging.info('Handling GET request: Processing content.')
            content = self.request.get('content')
            content = escape_html(content)

            bad_profanity = ['fuck', 'shit', 'cunt']
            ok_profanity = ['bastard', 'bitch', 'crap']

            bad_filter = ProfanitiesFilter(bad_profanity, 1, replacements="-",
                     complete = True, inside_words = True)
            content = bad_filter.clean(content)

            ok_filter = ProfanitiesFilter(ok_profanity, 2, replacements="-",
                     complete = True, inside_words = True)
            content = ok_filter.clean(content)

            logging.info('CONTENT: ' + content)

            self.write(content)

def escape_html(string):
    return cgi.escape(string, quote=True)


app = webapp2.WSGIApplication([('/', MainPage),
                            ('/check', ContentHandler)],
                            debug=True)

#def main():
#    webapp2.util.run_wsgi_app(application)

#if __name__ == "__main__":
#    main()
