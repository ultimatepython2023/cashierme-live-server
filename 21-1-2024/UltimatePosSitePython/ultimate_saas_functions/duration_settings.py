from flask import Flask
from app import *


def get_duration(sub_type):
    try:
        if sub_type == "Monthly":
            duration = 31

        elif sub_type == "yearly":
            duration = 366
        else:
            duration = 14
        return {"status": "Success", "duration": duration}
    except Exception as Error:
        print(Error)
        return {"status": "Error", "message": str(Error) }

