#! python3

import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import tkinter as tk
from tkinter import Tk, messagebox, Entry, Button, Checkbutton, IntVar, Toplevel, OptionMenu, Frame, StringVar, Scrollbar, Listbox
from tkinter import filedialog
from tkinter import *
from pathlib import Path
import numpy as np
import xlsxwriter
import xlrd
from scipy.interpolate import interp1d, UnivariateSpline
from scipy import integrate, stats
from tkcolorpicker import askcolor 
import six
from functools import partial
import math

import sqlite3
import datetime

"""
- connect to DB
- check if batch exists
- get foreign keys
- loop on samples in DATA list:
    - check if samplename matches with something in DB
    - check which cell it is
    - save in DB, with Fkeys
- disconnect
- message user

"""




#Connection to database
path =filedialog.askopenfilenames(title="Please select the DB file")[0]

db_conn=sqlite3.connect(path)
theCursor=db_conn.cursor()


#check if batch exists
#even if multiple batches loaded in same session. make list of batch name. check for every single one and create new list with the one existing in DB. tell the user for the others



