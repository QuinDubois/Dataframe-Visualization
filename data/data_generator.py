import csv
import random as rand
import numpy as np
import pandas as pd

'''
This file serves to generate pseudo-random datasets for demonstration purposes in the Dashboard app.
- Generates a csv file with fields "date", "value", and "ones" of length determined by 'data_length'
'''


def main():

    data_length = 100000

    df = pd.DataFrame({'ones': np.ones(data_length)})
    data = []
    num = 50
    for i in range(data_length):
        num = num + ((float(rand.randint(0, 200)) / 100) - 1)
        data.append(num)

    df.insert(loc=0, column="value", value=data)
    df['date'] = pd.date_range(start='1/1/1970', periods=len(df), freq='D')

    df.to_csv('data_file.csv', index=False)


if __name__ == "__main__":
    main()
