import json


class JSONHandler:
    def __init__(self, p_filename):
        self.filename = p_filename
        self.jsonpayload = ""

    def load(self):
        data = ''
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                f.close()
            return data
        except:
            print("Failed to load")
            return False

    def save(self):
        try:
            with open("config.dat", 'w+') as f:
                json.dump(self.jsonpayload, f, indent=4)
                f.close()
        except:
            print("Failed to Save")