import View.View
import traceback
import os

if __name__ == "__main__":
    entryPoint = View.View.PipelineControllerInterface()
    try:
        entryPoint.start()
    except Exception as e:
        tb = traceback.format_exc()
        if not os.path.exists("./logs"):
            os.mkdir("./logs")
        with open("./logs/error_logs.txt",'a') as stream:
            stream.write(tb)
        raise e