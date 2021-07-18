import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy
import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs
import random
import os
import time

class Data:
    def __init__(self, name, iso):
        self.name = name
        self.iso = iso
        self.democracy = None
        self.human_index = None
        self.gdp = None
    
    def __str__(self):
        return f"name\tiso\n{self.name}\t{self.iso}"
    
    def __bool__(self):
        return  self.name is not None and \
                self.iso is not None and \
                self.democracy is not None and \
                self.human_index is not None # and self.gdp is not None
    
    def contains_data(self):
        return self.democracy is not None or self.human_index is not None or self.gdp is not None
    
    
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
    
    # построение input.txt
    def build_input(self, k, stimul, time):

        self.k = k
        if self.show_errors:
            for x in self.data:
                if x.contains_data() and not x:
                    if x.democracy is None:
                        print(f"Отсутствует democracy у {x.name} {x.iso}")
                    if x.human_index is None:
                        print(f"Отсутствует human_index у {x.name} {x.iso}")
        data = [x for x in self.data if x]
        # print(data)
        # для format_output
        self.used_data_index = [i for i in range(len(self.data)) if self.data[i]]
        n = len(data)
        democracy = np.array([x.democracy for x in data])
        #democracy = (democracy - democracy.mean()) / democracy.std()
        #democracy /= max(democracy)
        #print(democracy)
        human_index = np.array([x.human_index for x in data])
        human_index = (human_index - human_index.mean()) / human_index.std()
        gdp = np.array([x.gdp for x in data])
        gdp = (gdp - gdp.mean()) / gdp.std()
        # print("gdp")
        # print(gdp)

        if self.show_errors:
            print("democracy:")
            print(democracy)
            print("human_index")
            print(human_index)
        matrix = [[0] * n for i in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                # matrix[i][j] = (gdp[i] - gdp[j]) ** 2
                matrix[i][j] = (democracy[i] - democracy[j]) ** 2
        mx = max(max(matrix[i] for i in range(len(matrix))))
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                matrix[i][j] /= mx
        stimul = max(max(matrix[i] for i in range(len(matrix)))) / 4
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                matrix[i][j] -= stimul
                matrix[i][j] *=  (gdp[i] - gdp[j]) ** 2


        with open('input.txt', 'w') as file:
            print(n, k, time, file=file)
            for row in matrix:
                print(*row, file=file)
                
    # обработка output.txt
    def format_output(self):
        with open("output.txt") as file:
            coalitions = list(map(int, file.readline().split()))
        self.iso_to_coalition = {}
        self.coalition_to_countries = [[] for i in range(self.k)]
        for used_index, coalition in zip(self.used_data_index, coalitions):
            iso_name = self.iso[used_index]
            y = self.iso_to_ind[iso_name]
            x = self.names[self.iso_to_ind[iso_name]]
            #print('len(coalition_to_countries) ', len(self.coalition_to_countries))
            #print('coalition ', coalition)
            self.coalition_to_countries[coalition].append(self.names[self.iso_to_ind[iso_name]])
            self.iso_to_coalition[iso_name] = coalition
        with open("Data/coalition_to_countries.txt", "w") as file:
            for i in range(self.k):
                print(*self.coalition_to_countries[i], file=file)
                
    # отрисовка
    def plot_output(self):
        colors = ['(230, 25, 75)', '(60, 180, 75)', '(255, 225, 25)', '(0, 130, 200)', '(245, 130, 48)', '(145, 30, 180)',
              '(70, 240, 240)', '(240, 50, 230)', '(210, 245, 60)', '(250, 190, 212)', '(0, 128, 128)',
              '(220, 190, 255)', '(170, 110, 40)', '(255, 250, 200)', '(128, 0, 0)', '(170, 255, 195)', '(128, 128, 0)',
              '(255, 215, 180)', '(0, 0, 128)', '(128, 128, 128)']
        while len(colors) < self.k:
            colors.append(str((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))))
        random.shuffle(colors)
        for i, color in enumerate(colors):
            color = color[1:-1].split(', ')
            color = tuple(map(lambda x: int(x) / 255, color))
            colors[i] = color
        plt.figure(figsize=(15, 10), dpi=80)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent([-150, 60, -25, 60])

        shpfilename = shpreader.natural_earth(resolution='110m',
                                              category='cultural',
                                              name='admin_0_countries')
        reader = shpreader.Reader(shpfilename)
        countries = reader.records()
        for country in countries:
            iso_name = country.attributes['ADM0_A3']
            if iso_name in self.iso_to_coalition:
                color = colors[self.iso_to_coalition[iso_name]]
                ax.add_geometries([country.geometry], ccrs.PlateCarree(),
                                  facecolor=color,
                                  label=country.attributes['ADM0_A3'])
            else:
                pass
#                 print(f"Нет никаких данных о стране {iso_name} в plot_output")
        # ax.add_feature(cartopy.feature.LAND)
        ax.add_feature(cartopy.feature.OCEAN)
        #ax.add_feature(cartopy.feature.COASTLINE)
        ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5)
        ax.add_feature(cartopy.feature.LAKES, alpha=0.95)
#         ax.add_feature(cartopy.feature.RIVERS)
        plt.show()
    
    def print_coalitions(self):
        print(*self.coalition_to_countries, sep='\n\n')
    # read iso
# added after Brunei
names = []
iso = []
with open("Data/iso.txt", encoding='utf-8') as file:
    for line in file:
        # ISO  NAME
        line = line.strip().split("\t")
        iso.append(line[0])
        names.append(line[1])
df = DF(names, iso, show_errors=False)
# read democracy index
# source https://en.wikipedia.org/wiki/Democracy_Index
tables = pd.read_html("https://en.wikipedia.org/wiki/Democracy_Index")
table = tables[5]
# print(table[['Country', '2020']])
names = table['Country'].to_list()
democracy_index = table['2020'].to_list()
for name, index in zip(names, democracy_index):
    df.get_by_name(name).democracy = index

# read human index
# source "https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D1%81%D1%82%D1%80%D0%B0%D0%BD_%D0%BF%D0%BE_%D0%B8%D0%BD%D0%B4%D0%B5%D0%BA%D1%81%D1%83_%D1%87%D0%B5%D0%BB%D0%BE%D0%B2%D0%B5%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B3%D0%BE_%D1%80%D0%B0%D0%B7%D0%B2%D0%B8%D1%82%D0%B8%D1%8F"
table = pd.read_csv("Data/human_development.txt", sep='\t', header=None)
table = table.drop(0, axis=1)
# print(table)
names = table[1].to_list()
democracy_index = table[2].to_list()
for name, index in zip(names, democracy_index):
    df.get_by_name(name).human_index = index

# read gdp
# source "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
table = pd.read_csv("Data/gdpdata.csv", sep='\t', header=None)
#print(table)
names = table[0].to_list()
gdp = table[1].to_list()
for name, index in zip(names, gdp):
    df.get_by_name(name).gdp = index


df.build_input(k=2, stimul=-0.5, time = 60)
df.format_output()
df.plot_output()
df.print_coalitions()