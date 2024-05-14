import os
import re
import pandas as pd
from langchain_openai import ChatOpenAI
import requests
from bs4 import BeautifulSoup
from io import BytesIO, StringIO
import urllib.request
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
import getpass
from typing import Optional, Type, Any
from pydantic import BaseModel, Field
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import sys
import time
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import streamlit as st
import base64
from langchain_groq import ChatGroq
