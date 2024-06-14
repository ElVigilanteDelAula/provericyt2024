from utils.utils import Utils
from database.database import Database
import numpy as np
import time
from datetime import datetime

sensors = ('http://127.0.0.1:100', 'http://127.0.0.1:101')
params = Utils.TEST_PARAMS

uid = datetime.now().strftime('%Y%m%d%H%M%S')
header = Database.get_header(sensors, params)

if __name__ =="__main__":
    db = Database('test.db')
    db.create_session(uid, header)
    try:
        while True:
            time.sleep(2)
            sensor_data = [Utils.get_data(sensor) for sensor in sensors]
            print(sensor_data) 

            db.record_data(uid, header, sensor_data)

    except KeyboardInterrupt:
        db.record_session_info(uid, sensors,'test')
        db.close()
        print("UnU")
    
