from flask import Flask, jsonify

import RPi.GPIO as GPIO

import werkzeug, time, sqlite3, datetime

from threading import Thread

app = Flask(__name__)
conn = sqlite3.connect('/home/pi/doorlock.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS doorlock (id INTEGER PRIMARY KEY AUTOINCREMENT, datetime TEXT NOT NULL)')
conn.close()


class DoorUnlock(Thread):
 
    def __init__(self, val):
        ''' Constructor. '''
        Thread.__init__(self)
        self.val = val

    def run(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(18, GPIO.OUT)
        GPIO.output(18, GPIO.HIGH)
        time.sleep(10)
        GPIO.output(18, GPIO.LOW)
        GPIO.cleanup()


@app.route('/unlock')
def unlock_door():
    app.logger.info("Got request")
    try:
        door_thread = DoorUnlock(1)
        door_thread.start()
    except:
        return jsonify({'status':'error', 'message':'Could not unlock the door'})
    conn = sqlite3.connect('/home/pi/doorlock.db')
    c = conn.cursor()
    c.execute("INSERT INTO doorlock (datetime) VALUES ('{}')".format(str(datetime.datetime.now())))
    conn.commit()
    conn.close()
    return jsonify({'status':'success', 'message':'The door has been unlocked'})


@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    return 'bad request!'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

