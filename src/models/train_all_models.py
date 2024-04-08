import src.models.train as tm

def main():

    for i in range(3, 4):
        print("Training model for station ", i, " ------------------------------------")  
        tm.train("./data/raw/mbajk_dataset.csv", "station_"+str(i))

if __name__ == '__main__':
    main()