import View.View
import traceback

if __name__ == "__main__":
    entryPoint = View.View.PipelineControllerInterface()
    try:
        entryPoint.start()
    except Exception as e:
        tb = traceback.format_exc()
        with open("error_logs.txt",'a') as stream:
            stream.write(tb)
        raise e