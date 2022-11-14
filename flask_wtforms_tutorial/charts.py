'''
This web service extends the Alphavantage api by creating a visualization module, 
converting json query results retuned from the api into charts and other graphics. 

This is where you should add your code to function query the api
'''
from logging import exception
from tracemalloc import start
import requests
#import lxml
import pygal
from datetime import datetime
from datetime import date
from datetime import timedelta
#from datetime import date
import sys
import math
# from dateutil.relativedelta import relativedelta
from json import JSONDecodeError
from flask import Flask, request, render_template

#Helper function for converting date
def convert_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()



# below function takes user input for date start and end
# gets every date in between them, inclusive
# has check for what user defined (weekly, monthly, etc.)

def getDateRange(start, end, timeSeries):
    if timeSeries == "1":
        start_date = str(start).split("-")
        end_date = str(end).split("-")
        start_date = datetime(int(start_date[0]), int(start_date[1]), int(start_date[2]), 0, 0, 0)
        end_date = datetime(int(end_date[0]), int(end_date[1]), int(end_date[2]), 20, 0, 0)
        dateRange = []
        delta = timedelta(minutes=5)
        while (start_date <= end_date):
            day = str(start_date.year) +'-'+str(start_date.month)+'-'+str(start_date.day) + " " + str(start_date.hour) +":"+ str(start_date.minute) + ":00"
            dateRange.append(day)
            start_date += delta
        return dateRange
    



    start_date = str(start).split("-")
    end_date = str(end).split("-")
    start_date = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
    end_date = date(int(end_date[0]), int(end_date[1]), int(end_date[2]))
    dateRange = []
    delta = timedelta(days=1)
    while (start_date <= end_date):
        day = str(start_date.year) +'-'+str(start_date.month)+'-'+str(start_date.day)
        dateRange.append(day)
        start_date += delta
    return dateRange

# def getInput():
#     inputs = []
#     while True:
#         symbol = input("What is the stock symbol for the company? ")
#         inputs.append(symbol)
#         while True:
#             try:
#                 chartType = int(input("What type of chart?\n1. Bar\n2. Line\nSelection: "))
#                 if chartType == 1 or chartType == 2:
#                     inputs.append(chartType)
#                     break
#                 else:
#                     print("Your options are 1 or 2")
#                     continue
#             except:
#                 print("Enter numbers 1 or 2 only")
#                 continue
#         while True:
#             try:
#                 timeSeries = int(input("What time series would you like to specify?\n1. Intraday\n2. Daily\n3. Weekly\n4. Monthly\nSelection: "))
#                 if timeSeries == 1 or timeSeries == 2 or timeSeries == 3 or timeSeries == 4:
#                     inputs.append(timeSeries)
        #             break
        #         else:
        #             print("Your options are 1, 2, 3, or 4")
        #             continue
        #     except:
        #         print("Enter numbers 1-4 only")
        #         continue
        # while True:
        #     try:
        #         start_Date = input("What is the start date? Format: YYYY-MM-DD: ")
        #         start_Date = str(datetime.datetime.strptime(start_Date, "%Y-%m-%d"))
        #         startDate = start_Date.split(' ')[0]
        #         break

        #     except ValueError:
        #         print('Please enter according to format')

        # inputs.append(startDate)

        # while True:
        #     try:
        #         end_Date = input("what is the end date? Format: YYYY-MM-DD: ")
        #         end_Date = str(datetime.datetime.strptime(end_Date, "%Y-%m-%d"))
        #         endDate = end_Date.split(' ')[0]
        #         if end_Date < start_Date:
        #             print("Start date must come before the End date")
        #             continue
        #         break
        #     except ValueError:
        #         print('Please enter according to format')

        # inputs.append(endDate)
        # return inputs
        
def apiCall(timeSeries,symbol):
    if timeSeries == "1":
        #https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=GOOGL&interval=5min&outputsize=full&apikey=TJ5UI0CUVXDLAV9K
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='+ symbol +'&outputsize=full&interval=5min&apikey=TJ5UI0CUVXDLAV9K'
        r = requests.get(url)
        try:
            data = r.json()
        except JSONDecodeError:
            print("Error Retriving JSON")
        return data


    if timeSeries == "2":
        # https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GOOGL&outputsize=full&apikey=TJ5UI0CUVXDLAV9K
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol='+ symbol +'&outputsize=full&interval=5min&apikey=TJ5UI0CUVXDLAV9K'
        r = requests.get(url)
        data = r.json()
        return data

    if timeSeries == "3":
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol='+ symbol +'&outputsize=full&interval=5min&apikey=TJ5UI0CUVXDLAV9K'
        r = requests.get(url)
        data = r.json()
        return data

    if timeSeries == "4":
        # https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GOOGL&outputsize=full&apikey=TJ5UI0CUVXDLAV9K
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol='+ symbol +'&outputsize=full&interval=5min&apikey=TJ5UI0CUVXDLAV9K'
        r = requests.get(url)
        data = r.json()
        return data

def parseJSON(rawJSON, timeSeries, dateRange):
    jsonDateRange = []
    xLabels = []

    if timeSeries == "1":
        #print("******", dateRange)
        for date in dateRange:
            try:
                splitEntry = date.split(' ')
                splitTime = splitEntry[1].split(':')
                hour = splitTime[0].zfill(2)
                minute = splitTime[1].zfill(2)
                second = splitTime[2].zfill(2)
                splitDate = splitEntry[0].split('-')
                month = splitDate[1].zfill(2)
                day = splitDate[2].zfill(2)
                date = splitDate[0] + '-' + month + '-' + day
                date = date + " " + hour + ":" + minute + ":" + second
                #print("\n",date)
                jsonDateRange.append(rawJSON['Time Series (5min)'][date])
                xLabels.append(date)
            except KeyError:
                continue
        buildGraph={"jsonDateRange":jsonDateRange, "xLabels":xLabels}

        return buildGraph

    if timeSeries == "2":
        for date in dateRange:
            try:
                splitDate = date.split('-')
                day = date.split('-')[2].zfill(2)
                date = splitDate[0] +'-'+splitDate[1].zfill(2)+'-'+ day
                jsonDateRange.append(rawJSON['Time Series (Daily)'][date])
                xLabels.append(date)
            except KeyError:
                continue
        buildGraph = {"jsonDateRange":jsonDateRange, "xLabels":xLabels}

        return buildGraph

    if timeSeries == "3":
        for date in dateRange:
            try:
                splitDate = date.split('-')
                day = date.split('-')[2].zfill(2)
                date = splitDate[0] +'-'+splitDate[1].zfill(2)+'-'+ day
                jsonDateRange.append(rawJSON['Weekly Time Series'][date])
                xLabels.append(date)
            except KeyError:
                continue
        buildGraph = {"jsonDateRange":jsonDateRange, "xLabels":xLabels}
        return buildGraph

    if timeSeries == "4":
        for date in dateRange:
            try:
                splitDate = date.split('-')
                day = date.split('-')[2].zfill(2)
                date = splitDate[0] +'-'+splitDate[1].zfill(2)+'-'+ day
                jsonDateRange.append(rawJSON['Monthly Time Series'][date])
                xLabels.append(date)
            except KeyError:
                continue
        buildGraph = {"jsonDateRange":jsonDateRange, "xLabels":xLabels}
        return buildGraph

def createGraph(jsonDateRange,timeSeries, xLabels, start, end,typeofgraph):
    # TODO append date range to title as well
    # TODO capture lowest and highest range in the data so can use map()
    openList = []
    highList = []
    lowList = []
    closeList = []
    volumeList = []
    categories = list(jsonDateRange[0].keys())
#return 
    if timeSeries == "1":
        title = "Time Series (5min) " + start + " - " + end
    if timeSeries == "2":
        title = "Time Series (Daily) " + start + " - " + end
    if timeSeries == "4":
        title = "Montly Time Series " + start + " - " + end
    if timeSeries == "3":
        title = "Weekly Time Series " + start + " - " + end

    minimum = 9999999
    maximum = 0
    for entry in jsonDateRange:
        if float(entry['3. low']) < minimum:
            minimum = float(entry['3. low'])
    for entry in jsonDateRange:
        if float(entry['2. high']) > maximum:
            maximum = float(entry['2. high'])
    for i in range(0,len(jsonDateRange)-1):
        openList.append(float(jsonDateRange[i]['1. open']))
        highList.append(float(jsonDateRange[i]['2. high']))
        lowList.append(float(jsonDateRange[i]['3. low']))
        closeList.append(float(jsonDateRange[i]['4. close']))
        #volumeList.append(float(jsonDateRange[i]['5. volume']))

    if typeofgraph == "1":
        bar_chart = pygal.Bar(x_label_rotation=90)
        bar_chart.title = title
        bar_chart.x_labels = xLabels
            #line_chart.y_labels = map(str, range(math.floor(minimum), math.ceil(maximum)))
        bar_chart.add(categories[0], openList)
        bar_chart.add(categories[1], highList)
        bar_chart.add(categories[2], lowList)
        bar_chart.add(categories[3], closeList)
            #line_chart.add(categories[4], volumeList)
        #bar_chart.render_in_browser()
        graph_data = bar_chart.render_data_uri()
        return graph_data

    if typeofgraph == "2":
        line_chart = pygal.Line(x_label_rotation=35)
        line_chart.title = title
        line_chart.x_labels = xLabels
        #line_chart.y_labels = map(str, range(math.floor(minimum), math.ceil(maximum)))
        line_chart.add(categories[0], openList)
        line_chart.add(categories[1], highList)
        line_chart.add(categories[2], lowList)
        line_chart.add(categories[3], closeList)
        #line_chart.add(categories[4], volumeList)
        #line_chart.render_in_browser()
        graph_data = line_chart.render_data_uri()
        return graph_data

def run(time_series, symbol, start_date, end_date, chart_type):
    #choice = "y"
    #timeSeriesChoice = {1: "INTRADAY",2:"DAILY",3:"WEEKLY",4:"MONTHLY"}
    #while choice == "y":
    #inputs = getInput()
    start_date = convert_date(str(start_date))
    end_date = convert_date(str(end_date))
    dateRange = getDateRange(start_date, end_date, time_series)
    data = apiCall(time_series, symbol)
    #print("******",data)
    buildGraph = parseJSON(data, time_series, dateRange)
    #print('Date Not Valid')
    jsonDateRange = buildGraph["jsonDateRange"]
    #print('Error Building Graph')
    xLabels = buildGraph["xLabels"]
    #print('Error adding labels')

    chart = createGraph(jsonDateRange, time_series,xLabels,str(start_date), str(end_date), chart_type)
    return chart
    #choice = input("Would you like to select another company? ").lower()
    #print(data["Monthly Time Series"]["2022-10-20"])
# if __name__ == "__main__":
#     main()

