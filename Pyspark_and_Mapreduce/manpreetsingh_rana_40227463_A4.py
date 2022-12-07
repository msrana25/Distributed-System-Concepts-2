import os
from itertools import permutations
import itertools
from pyspark import RDD, SparkContext
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import year, month, dayofmonth
from pyspark.sql.functions import desc
from pyspark.sql.functions import mean
from pyspark.sql.functions import col


def restaurant_shift_coworkers(worker_shifts: RDD) -> RDD:
    """
    Takes an RDD that represents the contents of the worker_shifts.txt. Performs a series of MapReduce operations via
    PySpark to calculate the number of shifts worked together by each pair of co-workers. Returns the results as an RDD
    sorted by the number of shifts worked together THEN by the names of co-workers in a DESCENDING order.
    :param worker_shifts: RDD object of the contents of worker_shifts.txt.
    :return: RDD of pairs of co-workers and the number of shifts they worked together sorted in a DESCENDING order by
             the number of shifts then by the names of co-workers.
             Example output: [(('Shreya Chmela', 'Fabian Henderson'), 3),
                              (('Fabian Henderson', 'Shreya Chmela'), 3),
                              (('Shreya Chmela', 'Leila Jager'), 2),
                              (('Leila Jager', 'Shreya Chmela'), 2)]
    """
    # raise NotImplementedError('Your Implementation Here.')
    data = worker_shifts.map(lambda x: [x.split(',')[0], x.split(',')[1], 1])  # [str, str, int]

    # Stored the names of worker(s) in the list in RDD grouped on basis of date of shift.
    # Output: ((str,int),[str])
    date_mapped = data.map(lambda x: ((x[1], x[2]), x[0])).groupByKey().mapValues(list)

    '''created all the permutations for 2 workers(ignored days where only a single worker was working
        (by emptying the worker name list for that particular date)) working together on a single date of shift'''
    # Output: ((str,int),(str,str))
    generate_pairs = date_mapped.map(
        lambda x: ((x[0][0], x[0][1]), list(itertools.permutations(x[1], 2)))).flatMapValues(
        lambda x: x)

    # Counted all the scenarios for same worker pairs for the same day.
    # Output: ((str,str), int)
    final_output = generate_pairs.map(lambda x: ((x[1][0], x[1][1]), 1)).groupByKey().mapValues(len).map(
        lambda x: ((x[0][0], x[0][1]), x[1]))

    # Sorted the output as per Problem 1 requirement
    sorted_output = final_output.sortBy(lambda x: [x[1], x[0]], ascending=False)
    return sorted_output


def air_flights_most_canceled_flights(flights: DataFrame) -> str:
    """
    Takes the flight data as a DataFrame and finds the airline that had the most canceled flights on Sep. 2021
    :param flights: Spark DataFrame of the flights CSV file.
    :return: The name of the airline with most canceled flights on Sep. 2021.
    """
    filtered_data = flights.filter(
        (flights.Cancelled == True) & (month(flights.FlightDate) == 9) & (year(flights.FlightDate) == 2021))
    required_columns = filtered_data.select('FlightDate', 'Airline', 'Cancelled')
    output = required_columns.groupBy("Airline").count().sort(desc("count")).take(1)
    return output[0].Airline


def air_flights_diverted_flights(flights: DataFrame) -> int:
    """
    Takes the flight data as a DataFrame and calculates the number of flights that were diverted in the period of 
    20-30 Nov. 2021.
    :param flights: Spark DataFrame of the flights CSV file.
    :return: The number of diverted flights between 20-30 Nov. 2021.
    """
    filtered_data = flights.filter(
        (flights.Diverted == True) & (month(flights.FlightDate) == 11) & (year(flights.FlightDate) == 2021) & (
                    dayofmonth(flights.FlightDate) >= 20))
    filtered_columns = filtered_data.select('Airline')
    output = filtered_columns.count()
    return output


def air_flights_avg_airtime(flights: DataFrame) -> float:
    """
    Takes the flight data as a DataFrame and calculates the average airtime of the flights from Nashville, TN to 
    Chicago, IL.
    :param flights: Spark DataFrame of the flights CSV file.
    :return: The average airtime average airtime of the flights from Nashville, TN to 
    Chicago, IL.
    """
    filtered_data = flights.filter(
        (flights.OriginCityName == 'Nashville, TN') & (flights.DestCityName == 'Chicago, IL'))
    intermediate_output = filtered_data.select(mean(col('Airtime'))).collect()
    extracted_mean = intermediate_output[0].asDict()['avg(Airtime)']
    return extracted_mean


def air_flights_missing_departure_time(flights: DataFrame) -> int:
    """
    Takes the flight data as a DataFrame and find the number of unique dates where the departure time (DepTime) is 
    missing.
    :param flights: Spark DataFrame of the flights CSV file.
    :return: the number of unique dates where DepTime is missing. 
    """
    filtered_data = flights.where(flights.DepTime.isNull())
    unique_days = filtered_data.select('FlightDate').distinct().count()
    return unique_days


def main():
    # initialize SparkContext and SparkSession
    sc = SparkContext('local[*]')
    spark = SparkSession.builder.getOrCreate()

    print('########################## Problem 1 ########################')
    # problem 1: restaurant shift coworkers with Spark and MapReduce
    # read the file
    worker_shifts = sc.textFile('worker_shifts.txt')
    sorted_num_coworking_shifts = restaurant_shift_coworkers(worker_shifts)
    # print the most, least, and average number of shifts together
    '''If the Problem 1 fails for the error "py4j.protocol.Py4JJavaError: An error occurred while calling 
     z:org.apache.spark.api.python.PythonRDD.runJob." or for "connection reset error" or any other error, 
     please comment the sorted_num_coworking_shifts.persist() method below. 
     Once commented and re-run the Problem 1 task will execute "'''
    # sorted_num_coworking_shifts.persist()
    print('Co-Workers with most shifts together:', sorted_num_coworking_shifts.first())
    print('Co-Workers with least shifts together:', sorted_num_coworking_shifts.sortBy(lambda x: (x[1], x[0])).first())
    print('Avg. No. of Shared Shifts:', sorted_num_coworking_shifts.map(lambda x: x[1]).reduce(
        lambda x, y: x + y) / sorted_num_coworking_shifts.count())

    print('########################## Problem 2 ########################')
    # problem 2: PySpark DataFrame operations
    # read the file
    flights = spark.read.csv('Combined_Flights_2021.csv', header=True, inferSchema=True)
    print('Q1:', air_flights_most_canceled_flights(flights), 'had the most canceled flights in September 2021.')
    print('Q2:', air_flights_diverted_flights(flights),
          'flights were diverted between the period of 20th-30th November 2021.')
    print('Q3:', air_flights_avg_airtime(flights),
          'is the average airtime for flights that were flying from Nashville to Chicago.')
    print('Q4:', air_flights_missing_departure_time(flights),
          'unique dates where departure time (DepTime) was not recorded.')


if __name__ == '__main__':
    main()
