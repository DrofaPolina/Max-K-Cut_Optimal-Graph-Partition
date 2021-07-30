import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy
import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs
import random
import os
import time
import math
from sklearn import preprocessing

class Data:
    def __init__(self, name, iso):
        self.name = name
        self.iso = iso
        self.num = None
    
    def __str__(self):
        return f"name\tiso\n{self.name}\t{self.iso}"
    
    def __bool__(self):
        return  self.name is not None and self.iso is not None
    
    def contains_data(self):
        return self.democracy is not None or self.human_index is not None
    
    
class DF:
    def __init__(self, names, iso, show_errors=False):
        assert len(names) == len(iso)
        self.show_errors = show_errors
        self.names = names
        self.iso = iso
        self.data = []
        self.iso_to_ind = {}
        self.name_to_ind = {}
        i = 0
        for iso_name, name in zip(self.iso, self.names):
            if iso_name in self.iso_to_ind:
                self.name_to_ind[name] = self.iso_to_ind[iso_name]
            else:
                self.iso_to_ind[iso_name] = i
                self.name_to_ind[name] = i
                self.data.append(Data(name, iso_name))
                i += 1
        self.dummy = Data("", "")
        
    # вернуть Data по имени
    def get_by_name(self, name):
        if name not in self.name_to_ind:
            if self.show_errors:
                print(f"{name} not found in self.name_to_ind")
            return self.dummy
        return self.data[self.name_to_ind[name]]
    
    # вернуть Data по iso
    def get_by_iso(self, iso_name):
        if iso_name not in self.iso_to_ind:
            if self.show_errors:
                print(f"{iso_name} not found in self.iso_to_ind")
            return self.dummy
        return self.data[self.iso_to_ind[iso_name]]


def is_close(a, b):
    return abs(a - b) < 1e-5

def check_close_values(dist):
    for i in range(n):
        for j in range(i):
            try:
                assert is_close(dist[i][j], dist[j][i])
            except AssertionError:
                # print(i, j, dist[i][j], dist[j][i], 'AE')
                dist[i][j] = dist[j][i] = (dist[i][j] + dist[j][i]) / 2
        try:
            assert dist[i][i] == 0
        except AssertionError:
            print(i, i, dist[i][i])
    return dist
        

def build_input(k, dist_matrix):
    dist_matrix = check_close_values(dist_matrix)
    n = len(dist_matrix)
    with open('input.txt', 'w') as file:
        print(n, k, file=file)
        for row in dist_matrix:
            print(*row, file=file)
#big_table = pd.read_csv("Data/Gravity_V202102.csv", sep = ',', usecols=["iso3_o",

big_table = pd.read_csv("Data/compressed_gravity.csv", sep = ',', usecols=["iso3_o",
                                                                        "iso3_d",])

big_table.dropna()
col_to_ind = dict(zip(big_table.columns, range(len(big_table.columns))))
ind_to_iso = list(set(big_table['iso3_o']))


with open("Data/iso_to_ind.txt", 'w') as file:
    n = len(ind_to_iso)
    iso_to_ind = {}
    for i, key in enumerate(ind_to_iso):
        iso_to_ind[key] = i
        print(key, i, file = file)

name_to_iso = {}
with open("Data/iso.txt") as file:
    for line in file:
        # ISO  NAME
        line = line.strip().split("\t")
        name_to_iso[line[1]] = line[0]

# read gdp
# source "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
iso_to_gdp = {}
table = pd.read_csv("Data/gdpdata.csv", sep='\t', header=None)
#table = table.drop(0, axis=1)
names = table[0].to_list()
gdp = table[1].to_list()
for name, val in zip(names, gdp):
    iso = name_to_iso[name]
    iso_to_gdp[iso] = val
gdp = np.array(gdp)

values = big_table.values


dist = [[0.0] * n for i in range(n)]
height = big_table.shape[0]

for line in values:
    iso1, iso2 = line[0], line[1]
    if iso1 == iso2:
        continue
    if iso1 not in iso_to_ind or iso2 not in iso_to_ind:
        continue

    ind1, ind2 = iso_to_ind[iso1], iso_to_ind[iso2]
    if iso1 in iso_to_gdp and iso2 in iso_to_gdp:
        dist[ind1][ind2] = abs(iso_to_gdp[iso1] - iso_to_gdp[iso2])
    else:
        dist[ind1][ind2] = gdp.std()

build_input(k=3, dist_matrix = dist)

