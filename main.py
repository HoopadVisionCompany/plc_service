from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from threading import Thread
from dotenv import load_dotenv
import os
import sys

print(0)
from src.controller_backend.router import router as controller_router
from src.pin.router import router as pin_router
from src.task.router import router as task_router
from src.scenario.router import router as scenario_router
from src.utils.middlewares.exception_middlewares import ExceptionMiddleware
from src.subscriber.redis_subscriber import subscriber_handler
from src.scenario.initialize_scenario import initialize
from src.setting.router import router as setting_router
print(00)

load_dotenv()

help_text = '''Chose one of the command: 
    runserver:      run fast api server
    rungrpcbackend: run grpc backend server
    runtest:        run tests
'''
app_gate = FastAPI()
app_gate.add_middleware(ExceptionMiddleware)
app_gate.include_router(controller_router, tags=["controller"])
app_gate.include_router(pin_router, tags=["pin"])
app_gate.include_router(task_router, tags=["task"])
app_gate.include_router(scenario_router, tags=["scenario"])
app_gate.include_router(setting_router, tags=["setting"])


origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app_gate.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_server():
    uvicorn.run(app_gate, host=os.getenv("UVICORN_HOST"), port=int(os.getenv("UVICORN_PORT")))


def run_subscriber():
    print(12)
    subscriber_handler()


def run_initialize_scenarios():
    initialize()


def run_all():
    thread_run_server = Thread(target=run_server, args=())
    # thread_subscriber = Thread(target=run_subscriber, args=())
    thread_run_server.start()
    # thread_subscriber.start()
    thread_run_server.join()
    # thread_subscriber.join()


def runner():
    if len(sys.argv) >= 2:
        if sys.argv[1] == '--all':
            run_all()
        if sys.argv[1] == '--scenario':
            run_initialize_scenarios()
        # elif sys.argv[1] == 'runserver':
        #     run_server()
        # elif sys.argv[1] == 'subscriber':
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
