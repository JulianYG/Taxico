from collections import defaultdict as ddict
import gmaps
import gmplotlib
import plotly.plotly as py
import plotly.graph_objs as go
from utils import *
import random
from colour import Color

gmaps.configure(api_key="AIzaSyCB9rVMgEbTcYaQhnbM6jBzLjFLXLaGJZ8")
 
def plot_log_histogram(b):
    data = go.Histogram(x=b)
    layout = go.Layout(yaxis=dict(type='log', autorange=True))
    fig = go.Figure(data=[data], layout=layout)
    py.iplot(fig)

def plot_histogram(b):
    data = [go.Histogram(x=b)]
    py.iplot(data)
     
def plot_probability_map():
    timeMap = ddict(list)
    maps = []
    for i in range(24):
        maps.append(gmaps.Map())
     
    with open('params/probmap', 'r') as data:
        reader = csv.reader(data, delimiter=',')
        for row in reader:
            lat0 = row[2].replace("'", "")
            lat1 = row[3].replace("'", "")
            lon0 = row[0].replace("'", "")
            lon1 = row[1].replace("'", "")
            weight = float(row[-1].replace("'", ""))
            time = int(row[4].replace("'", ""))
            dot = centerize_grid(((lon0, lon1), (lat0, lat1)))
            point = (dot[1], dot[0], weight)
            timeMap[time].append(point)
     
    overlapped_map = gmaps.Map()
    for i in range(24):
        data = timeMap[i]
        heatmap_layer = gmaps.WeightedHeatmap(data=data)
        heatmap_layer.max_intensity = 1
        maps[i].add_layer(heatmap_layer)
        overlapped_map.add_layer(heatmap_layer)
 
    overlapped_map

def plot_dropoff_distribution():
    timeLocMap = ddict(list)
    with open('params/dropmap', 'r') as data:
        reader = csv.reader(data, delimiter=',')
        for row in reader:
            dot = centerize_grid(((row[0], row[1]), (row[2], row[3])))
            locs = row[5].split(' ')
            for loc in locs:
                coords = loc.split(':')
                timeLocMap[(int(row[4]), dot)].append((float(coords[1]), float(coords[0])))
                # lat, lon
    gmap = gmaps.Map()
    start = random.choice(timeLocMap.keys())
    print start
    print timeLocMap[start]
    pickup_layer = gmaps.symbol_layer([(start[1][1], start[1][0])], fill_color='green', 
        stroke_color='green', scale=2)
    dropoff_layer = gmaps.Heatmap(data=timeLocMap[start])
    gmap.add_layer(pickup_layer)
    gmap.add_layer(dropoff_layer)
    gmap

def read_count_map(name):
    countMap = ddict(dict)
    with open(name, 'r') as data:
        reader = csv.reader(data, delimiter=',')
        for row in reader:
            key = (((row[0], row[1]), (row[2], row[3])), row[4])
            dist_list, time_list, pay_list = row[5].split(' '), \
                row[6].split(' '), row[7].split(' ')
            dist_cnt, time_cnt, pay_cnt = [], [], []
            for d in dist_list:
                dist_tup = d.split(':')
                for i in range(int(dist_tup[1])):
                    dist_cnt.append(float(dist_tup[0])) 
            for t in time_list:
                time_tup = t.split(':')
                for i in range(int(time_tup[1])):
                    time_cnt.append(float(time_tup[0]))
            for p in pay_list:
                pay_tup = p.split(':')
                for i in range(int(pay_tup[1])):
                    pay_cnt.append(float(pay_tup[0]))
                
            countMap['dist'][key] = dist_cnt
            countMap['time'][key] = time_cnt
            countMap['pay'][key] = pay_cnt
    return countMap

def plot_learning_curve(filename):
    x, y = [], []
    with open(filename, 'r') as data:
        reader = csv.reader(data, delimiter=' ')
        for row in reader:
            if len(row) == 2:
                x.append(row[1])
            if len(row) == 1:
                y.append(row[0])
    trace = go.Scatter(x=x, y=y, mode='lines+markers')
    data = [trace]
    py.iplot(data, filename='learning_curve')


def path_visualization(filename):
    path = read_path(filename)
    for route in path:
        plot_route([(centerize_grid(l[0]), l[1], 
            "%.2f" % l[2]) for l in route['loc']], '%.2f' % route['profit'])

def plot_route(locations, title):
    gmap = gmplotlib.GoogleMapPlotter(40.7530427, -73.9372376, 11.22)
    gmap.grid(40.616669, 40.886116, 0.00444, -74.021611, -73.742833, 0.00444)
    n = len(locations)
    c = list(Color('cornsilk').range_to(Color('darkred'), n))
    for i in range(n):
        l = locations[i]
        gmap.marker(l[0][1], l[0][0], c=int(c[i].get_hex_l()[1:], 16), 
            title=(str(i), 'Earned %s at %s' % (l[2], l[1])))
    gmap.draw(title + '.html')

# cmap = read_count_map('params/countmap')
# dist_to_plot = cmap['dist']
# grid_hr_key = random.choice(dist_to_plot.keys())
# print grid_hr_key, len(dist_to_plot[grid_hr_key]), 'dist'
# # print catogery_to_plot[grid_hr_key]
# plot_histogram(dist_to_plot[grid_hr_key])

# time_to_plot = cmap['time']
# grid_hr_key = random.choice(time_to_plot.keys())
# print grid_hr_key, len(time_to_plot[grid_hr_key]), 'time'
# # print catogery_to_plot[grid_hr_key]
# plot_histogram(time_to_plot[grid_hr_key])

# money_to_plot = cmap['pay']
# grid_hr_key = random.choice(money_to_plot.keys())
# print grid_hr_key, len(money_to_plot[grid_hr_key]), 'pay'
# # print catogery_to_plot[grid_hr_key]
# plot_histogram(money_to_plot[grid_hr_key])

path_visualization('route')
