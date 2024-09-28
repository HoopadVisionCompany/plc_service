from fastapi import FastAPI
import uvicorn
from threading import Thread
from dotenv import load_dotenv
import os
import sys

print(0)
from src.plc.router import router as plc_router
from src.pin.router import router as pin_router
from src.task.router import router as task_router
from src.utils.middlewares.exception_middlewares import ExceptionMiddleware

print(00)

load_dotenv()

help_text = '''Chose one of the command: 
    runserver:      run fast api server
    rungrpcbackend: run grpc backend server
    runtest:        run tests
'''
app_gate = FastAPI()
app_gate.add_middleware(ExceptionMiddleware)
app_gate.include_router(plc_router, tags=["plc"])
app_gate.include_router(pin_router, tags=["pin"])
app_gate.include_router(task_router, tags=["task"])



def run_server():
    uvicorn.run(app_gate, host=os.getenv("UVICORN_HOST"), port=int(os.getenv("UVICORN_PORT")))


def run_all():
    thread_run_server = Thread(target=run_server, args=())
    thread_run_server.start()
    thread_run_server.join()


def runner():
    if len(sys.argv) >= 2:
        if sys.argv[1] == '--all':
            run_all()
        elif sys.argv[1] == 'runserver':
            run_server()
        # elif sys.argv[1] == 'rungrpcbackend':
        #     run_grpc_backend()
        # elif sys.argv[1] == 'runtest':
        #     pass
        elif sys.argv[1] == '--help':
            print(help_text)
        else:
            print('''some thing is wrong:
            please type --help''')


if __name__ == "__main__":

    runner()
