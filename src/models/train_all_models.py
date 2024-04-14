import src.models.train as tm

def main():

    for i in range(1,30):
        print("Training model for station ", i, " ------------------------------------")  
        tm.train("./data/processed/station_"+str(i)+".csv", "station_"+str(i), windowsize=8,test_size_multiplier = 5 )

if __name__ == '__main__':
    main()