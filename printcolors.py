from termcolor import colored, cprint
# Printing Colors
class prt:
    def warning(self,text):
        text = '[WARG]:' + text
        cprint(text, 'yellow', attrs=['reverse','bold'])

    def error(self,text):
        text = '[ERR]:' + text
        cprint(text, 'red', attrs=['bold'])

    def succful(self,text):
        text = '[OK]:' + text
        cprint(text, 'green', attrs=['reverse','bold'])

    def service(self, text):
        text = '[SEX]:' + text
        cprint(text, 'blue', attrs=['bold'])
    def api(self,text):
        text = '[API]:' +text
        cprint(text, 'magenta', attrs=['bold'])
    def runtime(self,text):
        text='[RT]:'+text
        cprint(text,'cyan',attrs=['bold'])

