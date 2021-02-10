
from flask import Flask, render_template, redirect, request, flash, send_file
from hinScraperCSV import scrape_csv
from werkzeug.utils import secure_filename
from blobLogging import createBlobLog
from tableStorage import tableStorage

import urllib3
from datetime import date
from random import randint
import os, logging, time
import config

# App config values
DEBUG=True
app = Flask(__name__)
app.config.from_object(__name__)
#app.config['SECRET_KEY'] = 
# Use "/" Forward slashes to avoid unicode error
app.config["CSV_UPLOADS"] = os.path.join(app.root_path, 'static', 'uploads')
app.config["LOG_PATH"] = os.path.join(app.root_path, 'static', 'logs')
app.config["TEMPLATE_PATH"] = os.path.join(app.root_path, 'static', 'uploads', 'hin_template.csv')
app.config["ALLOWED_EXTENSIONS"] = ["CSV"]
app.config["MAX_FILESIZE"] = 8 * 1024 * 1024    #~8mb limit
today = date.today()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurations
azure_table_name = config.AZURE['STORAGE_TABLE_NAME']



# Define allow_extension() function checks if the filename's extension is allowed
def allowed_extension(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_EXTENSIONS"]:
        return True
    else:
        return False

# Define allowed_filesize() function checks if the filesize exceeds the maximum limit
# defined in the app.config["MAX_FILESIZE"]
def allowed_filesize(filesize):

    if int(filesize) <= app.config["MAX_FILESIZE"]:
        return True
    else:
        return False


@app.route("/home")
def home():
    return render_template('home.html')

"""
Receives a request to process a csv file
"""
@app.route("/")
@app.route("/upload-csv", methods=["GET", "POST"])
def upload_csv():
    try:

        if request.method == "POST":

            if  not os.path.isdir(app.config["LOG_PATH"]):
                print("doesn't exist")
                os.makedirs(app.config["LOG_PATH"])

            # Initializing the logging object and naming the log that will be created
            # Logging begins here
            today = date.today()
            logFileName = str(date.today().strftime("%m-%d-%Y")) + "_log.csv"
            logging.basicConfig(filename=os.path.join(app.config["LOG_PATH"], logFileName),
                format='%(asctime)s %(levelname)-8s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filemode='w')
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            t0 = time.time()

            if request.files:

                if not allowed_filesize(request.cookies.get("filesize")):
                    flask("File exceeded maximum size", "danger")
                    print("File exceeded maximum size")
                    return redirect(request.url)

                #name attribute in html is [name=csv]
                csv = request.files["csv"]

                if csv.filename == "":
                    print("No filename")
                    flask("File must be named correctly", "danger")
                    return redirect(request.url)

                if allowed_extension(csv.filename):
                    filename = secure_filename(str(today) + csv.filename)
                    filepath = os.path.join(app.config["CSV_UPLOADS"], filename)
                    if not (os.path.exists(filepath)):
                        print("No duplicates")
                    else:
                        print("Duplicates")
                        filename = secure_filename(str(today) + "_" + str(randint(1,999)) + "_" + csv.filename)
                        filepath = os.path.join(app.config["CSV_UPLOADS"], filename)
                    csv.save(filepath)
                    print(csv)
                    print("csv saved\n")

                    # Call hinScraperCSV.py function scrape_csv to begin scraping hin information
                    output = scrape_csv(filepath)
                    print(output)
                    print(output[1])

                    # Timing savings calculated and logged
                    hinsProcessed = output[1]
                    t1 = time.time()
                    totalTime = t1-t0
                    timeByUser = hinsProcessed * 60
                    timeSaved = timeByUser - totalTime
                    
                    logger.info("Total Hins processed: " + str(hinsProcessed))
                    logger.info("Time by system: " + str(totalTime))
                    logger.info("Time Saved: " + str(timeSaved))
                    logger.info("**End of logging**")
                    #logging.shutdown

                    print(str(today.strftime("%Y")))
                    print(str(today.strftime("%m-%d")))

                    # Calls tableStorage.py function to create database entity for the information collected above
                    tableStorage(azure_table_name, str(today.strftime("%Y")), str(today.strftime("%m-%d")), hinsProcessed, timeSaved, totalTime, timeByUser, 1)

                    # Send log file to blob storage
                    container_name = "hin-logs-" + str(today.strftime("%m-%Y"))
                    createBlobLog(container_name, (os.path.join(app.config["LOG_PATH"], logFileName)), logFileName)

                    # Define generate() function will open the file being served up and will remove it after.
                    def generate():
                        with open(filepath) as f:
                            yield from f
                        os.remove(filepath)

                    r = app.response_class(generate(), mimetype='text/csv')
                    r.headers.set('Content-Disposition', 'attachment', filename=filename)
                    return r
                else:
                    print("That file extension is not allowed")
                    flash("File must be in CSV format", "warning")
                    return redirect(request.url)

        return render_template("upload_csv.html")   
    except Exception as e:
        print(e)
        # **IMPROVEMENT IDEA**
        # Make a 404.html
        flash(e, "danger")
        return render_template("upload_csv.html")

@app.route('/download')
def download_file():
    try:
        path = app.config["TEMPLATE_PATH"]
        return send_file(path, as_attachment=True)
    except Exception as e:
        return render_template('about.html')

@app.route("/about")
def about():
    return render_template('about.html')

# App is ran from this statement
if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)