import csv

filename = "extra/reports/reports.csv"

def init():
  fields = ["postBool", "id", "repId", "time"]
  with open(filename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)

def write(postBool: bool, id:int, repId:int, time:str="undefined"):
  if (id == repId): return 0
  global filename
  with open(filename, 'a') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow([str(postBool), str(id), str(repId), time])
    return 1