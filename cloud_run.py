import threading
import cloud_reg
import cloud_service

t2= threading.Thread(name="reg run", target=cloud_reg.cloud_reg_run, args=(),daemon=True)
t2.start()

t1= threading.Thread(name="service run", target=cloud_service.cloud_service_run, args=(),daemon=True)
t1.start()
while True:
    pass
