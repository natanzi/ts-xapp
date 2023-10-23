from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import logging

app = Flask(__name__)

# Secret key for flashing messages and session management
app.secret_key = '11AB7SX3I0XparYHCoOVv25scQoj1FNrI7BQ2KU24yVtBKX'

# Set up logging
logging.basicConfig(filename='dashboard.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# The service URL for your ts-xApp in Kubernetes
TS_XAPP_URL = "http://ts-xapp-service:3000"  

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/trigger/<function_name>', methods=['POST'])
def trigger_function(function_name):
    try:
        response = requests.post(f"{TS_XAPP_URL}/{function_name}")
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        
        # If we got here, it means the request was successful
        message = response.json().get('message', 'Operation executed')
        flash(message, 'success')
        logging.info(f"Successfully triggered {function_name}. Message: {message}")

    except requests.RequestException as req_err:
        flash(f"Failed to trigger {function_name}. Error: {str(req_err)}", 'error')
        logging.error(f"Failed to trigger {function_name}. Error: {str(req_err)}")

    except Exception as gen_err:
        flash(f"An unexpected error occurred: {str(gen_err)}", 'error')
        logging.error(f"An unexpected error occurred while triggering {function_name}. Error: {str(gen_err)}")

    return redirect(url_for('index'))

if __name__ == '__main__':
    logging.info("Dashboard starting...")
    app.run(host='0.0.0.0', port=5000)  # Adjust port if needed