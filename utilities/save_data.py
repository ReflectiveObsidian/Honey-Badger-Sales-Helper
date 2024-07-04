FILENAME = 'data.txt'
class SaveData:
    def save(contents):
        with open(FILENAME, 'a') as f:
            f.write(contents + '\n')

    def load():
        with open(FILENAME, 'r') as f:
            return f.read()