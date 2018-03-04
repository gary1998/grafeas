
def get_home_page():
    with open('static/index.html', 'r') as f:
        data = f.read()
        return data