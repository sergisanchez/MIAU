from termcolor import colored, cprint
# Printing Colors
class prt:
    def warning(self,text):

        cprint(text, 'yellow', attrs=['reverse','bold'])

    def error(self,text):

        cprint(text, 'red', attrs=['bold'])

    def succful(self,text):

        cprint(text, 'green', attrs=['reverse','bold'])

    def service(self, text):
        cprint(text, 'blue', attrs=['bold'])
    def api(self, text):
        cprint(text, 'magenta', attrs=['bold'])

if __name__ == "__main__":
    printing=prt()
    printing.error('>>>>> Computing route <<<<<<<<')
