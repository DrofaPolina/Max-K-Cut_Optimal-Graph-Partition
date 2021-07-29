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


with open("output.txt") as file:
    id_to_coalition = list(map(int, file.readline().split()))

with open("input.txt") as file:
    n, k = list(map(int, file.readline().split()))

iso_to_ind = {}
with open("Data/iso_to_ind.txt") as file:
    for line in file:
      key, value = line.split()
      iso_to_ind[key] = int(value)

# Подбор цветов
colors = ['(255, 140, 0)', '(255, 69, 0)', '(154, 205, 50)', '(128, 128, 0)', '(85, 107, 47)',
              '(0, 128, 128)', '(70, 130, 180)', '(139, 69, 19)', '(105, 105, 105)']
random.shuffle(colors)


colors = [tuple(map(lambda x: int(x) / 255, color[1:-1].split(', '))) for color in colors]
while len(colors) < k:
    colors.append((random.random(), random.random(), random.random()))

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
    if iso_name in iso_to_ind:
        color = colors[id_to_coalition[iso_to_ind[iso_name]]]
    else:
        color = (1, 1, 1)
        print(f"Нет данных о стране {iso_name} в plot_output")
    ax.add_geometries([country.geometry], ccrs.PlateCarree(),
                      facecolor=color,
                      label=country.attributes['ADM0_A3'])

ax.add_feature(cartopy.feature.OCEAN)
ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5)
ax.add_feature(cartopy.feature.LAKES, alpha=0.95)
plt.show()