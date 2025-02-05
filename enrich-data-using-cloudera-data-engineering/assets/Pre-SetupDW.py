#****************************************************************************
# (C) Cloudera, Inc. 2020-2021
#  All rights reserved.
#
#  Applicable Open Source License: GNU Affero General Public License v3.0
#
#  NOTE: Cloudera open source products are modular software products
#  made up of hundreds of individual components, each of which was
#  individually copyrighted.  Each Cloudera open source product is a
#  collective work under U.S. Copyright Law. Your license to use the
#  collective work is as provided in your written agreement with
#  Cloudera.  Used apart from the collective work, this file is
#  licensed for your use pursuant to the open source license
#  identified above.
#
#  This code is provided to you pursuant a written agreement with
#  (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
#  this code. If you do not have a written agreement with Cloudera nor
#  with an authorized and properly licensed third party, you do not
#  have any rights to access nor to use this code.
#
#  Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
#  contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
#  KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
#  WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
#  IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
#  AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
#  ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
#  OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
#  CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
#  RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
#  BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
#  DATA.
#
#  Source File Name: Pre-SetupDW.py
#
#  REQUIREMENT: Update variable s3BucketPath
#               using storage.location.base attribute; defined by your environment.
#
# #  Description: As a prerequisite, we need to setup data warehouse with
#               fictitious sales, factory and customer data.
#               The following Hive tables will be created:
#                     DATABASE: SALES
#                       TABLES: CAR_SALES
#
#                     DATABASE: FACTORY
#                       TABLES: CAR_INSTALLS
#                               EXPERIMENTAL_MOTORS
#
#                     DATABASE: MARKETING
#                       TABLES: CUSTOMER_DATA
#                               GEO_DATA_XREF
#
# #  Author(s): Nicolas Pelaez, George Rueda de Leon
#***************************************************************************/
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import pyspark.sql.functions as F
import configparser
import os 
import sys
#-----------------------------------------------------------------------------------
# LOAD DATA FROM .CSV FILES ON AWS S3 CLOUD STORAGE
#
# REQUIREMENT: Update variable s3BucketPath
#              using storage.location.base attribute; defined by your environment.
#
#              For example, property storage.location.base
#                           has value 's3a://usermarketing-cdp-demo'
#                           Therefore, set variable as:
#                                 s3BucketPath = "s3a://usermarketing-cdp-demo"
#-----------------------------------------------------------------------------------
config = configparser.ConfigParser()
config.read('/app/mount/cde_examples.ini')
s3BucketPath = config['CDE-examples']['s3BucketPath'].replace('"','').replace("\'",'')
prefix = config['CDE-examples']['userPrefix'].replace('"','').replace("\'",'')

SALES_DB = prefix + "_SALES"
FACTORY_DB = prefix + "_FACTORY"
MARKETING_DB = prefix + "_MARKETING"

#---------------------------------------------------
#               CREATE SPARK SESSION
#---------------------------------------------------
spark = SparkSession.builder.appName('Ingest-' + prefix).getOrCreate()
spark.conf.set("spark.sql.legacy.allowCreatingManagedTableUsingNonemptyLocation", "true")
spark.conf.set("cde.gangScheduling.enabled", "true")

car_installs  = spark.read.csv(s3BucketPath + "/car_installs.csv",        header=True, inferSchema=True)
car_sales     = spark.read.csv(s3BucketPath + "/car_sales.csv",           header=True, inferSchema=True)
customer_data = spark.read.csv(s3BucketPath + "/customer_data.csv",       header=True, inferSchema=True)
factory_data  = spark.read.csv(s3BucketPath + "/experimental_motors.csv", header=True, inferSchema=True)
geo_data      = spark.read.csv(s3BucketPath + "/postal_codes.csv",        header=True, inferSchema=True)



#---------------------------------------------------
#       SQL CLEANUP: DATABASES, TABLES, VIEWS
#---------------------------------------------------
print("JOB STARTED...")
spark.sql("DROP DATABASE IF EXISTS " + SALES_DB + " CASCADE")
spark.sql("DROP DATABASE IF EXISTS " + FACTORY_DB + " CASCADE")
spark.sql("DROP DATABASE IF EXISTS " + MARKETING_DB + " CASCADE")
print("\tDROP DATABASE(S) COMPLETED")



##---------------------------------------------------
##                 CREATE DATABASES
##---------------------------------------------------
spark.sql("CREATE DATABASE " + SALES_DB)
spark.sql("CREATE DATABASE " + FACTORY_DB)
spark.sql("CREATE DATABASE " + MARKETING_DB)
print("\tCREATE DATABASE(S) COMPLETED")



#---------------------------------------------------
#               POPULATE TABLES
#---------------------------------------------------
car_sales.write.mode("overwrite").saveAsTable(SALES_DB + '.CAR_SALES', format="parquet")
car_installs.write.mode("overwrite").saveAsTable(FACTORY_DB + '.CAR_INSTALLS', format="parquet")
factory_data.write.mode("overwrite").saveAsTable(FACTORY_DB +'.EXPERIMENTAL_MOTORS', format="parquet")
customer_data.write.mode("overwrite").saveAsTable(MARKETING_DB + '.CUSTOMER_DATA', format="parquet")
geo_data.write.mode("overwrite").saveAsTable(MARKETING_DB + '.GEO_DATA_XREF', format="parquet")
print("\tPOPULATE TABLE(S) COMPLETED")

print("JOB COMPLETED.\n\n")
