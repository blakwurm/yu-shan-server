from flask import render_template
import connexion 

# Create the application instance
app = connexion.App(__name__, template_folder="templates")

#Read the swagger.yml file to configure the endpoints
app.add_api('swagger.yml')

# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:3000/

    :return:        the rendered template 'home.html'
    """
    return render_template('home.html')

def check_auth(username: str, password: str):
    print("username is " + username + " and pass is " + password)
    return True 

application = app

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)


