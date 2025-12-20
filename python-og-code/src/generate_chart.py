import termchart
import time
import os
from random import randint

graph = termchart.Graph([])
graph.setCols(200)
graph.setRows(30)
while True:
    rand = randint(1, 9)
    graph.addData(rand)
    graph.draw()
    os.system('cls' if os.name == 'nt' else 'clear')









# def generate_chart(self, wpm_list):
#         df = pd.DataFrame(wpm_list, columns=['wpm'])
#         # Calculate the maximum value in the 'wpm' column
#         max_wpm = df['wpm'].max()

#         # Create a list of empty strings to represent each row in the chart
#         rows = [' ' * len(df) for _ in range(20)]

#         # Loop over the rows in the DataFrame and add an 'x' to the appropriate position in the chart
#         for i, row in df.iterrows():
#             # Calculate the y position for this data point
#             y = int(row['wpm'] / max_wpm * 19)

#             # Add the 'x' to the appropriate position in the chart
#             rows[19 - y] = rows[19 - y][:i] + 'x' + rows[19 - y][i + 1:]

#         # Add the y-axis to the chart
#         for i in range(20):
#             rows[i] = '| ' + rows[i]

#         # Add the x-axis to the chart
#         rows.append('+ ' + '-' * len(df) + '\n')

#         # Convert the list of rows to a single string
#         chart = '\n'.join(rows)

#         print('\n' * 20)
#         print(chart, end='\r')


#     def generate_chart(self, data, height=20, width=80):
#         # Determine the maximum value in the data
#         max_val = max(data)

#         # Determine the number of data points to plot
#         num_points = min(len(data), width)

#         # Determine the x-axis tick interval
#         tick_interval = max(1, num_points // 10)

#         # Determine the maximum value for the y-axis
#         if len(data) >= height:
#             max_y = max_val
#         else:
#             max_y = data[0]

#         # Create a list of empty strings to represent each row in the chart
#         rows = [' ' * num_points for _ in range(height)]

#         # Loop over the data points and add an 'x' to the appropriate position in the chart
#         for i in range(num_points):
#             # Calculate the index of the data point to use for this position
#             index = int(i / num_points * len(data))

#             # Calculate the y position for this data point
#             y = int(data[index] / max_y * (height - 1))

#             # Add the 'x' to the appropriate position in the chart
#             rows[height - 2 - y] = rows[height - 2 - y][:i] + 'x' + rows[height - 2 - y][i + 1:]

#         # Add the y-axis ticks to the chart
#         for i in range(height - 1):
#             if i % (height // 10) == 0:
#                 rows[i] = '|' + rows[i][1:]
#             else:
#                 rows[i] = '|' + rows[i][1:]

#         # Add the x-axis ticks to the chart
#         for i in range(0, num_points, tick_interval):
#             rows[-1] = rows[-1][:i] + '-' + rows[-1][i + 1:]
#             rows[-2] = rows[-2][:i] + str(i) + rows[-2][i + 1 + len(str(i)):]

#         # Add the x-axis label to the chart
#         rows[-1] = rows[-1][:-1] + '+'

#         # Convert the list of rows to a single string
#         chart = '\n'.join(rows)
#         print(chart)
#         # return chart
