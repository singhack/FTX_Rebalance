import simplejson as json



def read_cofing():
    with open('config.json') as json_file:
        return json.load(json_file)

config = read_cofing()
apiKey= config["apiKey"]
print(apiKey)
