from django.shortcuts import render
from .models import Country

#Importing necessary dependencies
from datetime import *
import requests
import json
from bs4 import BeautifulSoup

#global variables
country_url = "https://api.covid19api.com/countries"
us_url = "https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/cases-in-us.html"
confirmed_url = "https://api.covid19api.com/country/{}/status/confirmed/live"
death_url = "https://api.covid19api.com/country/{}/status/deaths/live"
total_url = "https://api.covid19api.com/summary"

#method to get all country names (used in nav-menu)
def get_menu_context():
	all_countries = {}
	countries = Country.objects.all()
	for country in countries:
		if country.name == '':
			pass
		else:
			all_countries[country.name] = country.slug
	return all_countries

#The homepage view (Every country details)
def index(request):

	#variable declaration
	new_cases = 0
	total_cases = 0
	total_death = 0
	new_death = 0
	new_recovered = 0
	total_recovered = 0

	#Check for a new country entry and add it automatically to database
	response = requests.get(country_url).text
	country_json = json.loads(response)
	for elem in country_json:
		if Country.objects.filter(name=elem['Country']).exists():
			pass
		else:
			country = Country(name=elem['Country'], slug=elem['Slug'])
			country.save()

	#Gets details from the API
	response = requests.get(total_url).text

	#get the list of all countries (for nav-menu)
	all_countries = {}
	all_countries = get_menu_context()

	#get details
	stats = json.loads(response)
	stats = stats['Countries']
	for elem in stats:
		new_cases += elem['NewConfirmed']
		total_cases += elem['TotalConfirmed']
		total_death += elem['TotalDeaths']
		new_death += elem['NewDeaths']
		new_recovered += elem['NewRecovered']
		total_recovered += elem['TotalRecovered']
	context = {
		'total_cases':total_cases,
		'total_death':total_death,
		'new_death':new_death,
		'total_recovered':total_recovered,
		'new_recovered':new_recovered,
		'new_cases':new_cases,
		'all_countries':all_countries,
	}
	return render(request, 'all.html', context=context)

#view for a particular country
def country(request, country_name):

	#get the list of all countries (for nav-menu)
	all_countries = {}
	all_countries = get_menu_context()

	#Alternative method for US. The API had data of each province. But, we need 
	#the summary data of whole nation.
	if country_name == "us":
		response = requests.get(us_url).text
		soup = BeautifulSoup(response,'html.parser')
		data_soup = soup.find('div',{'class':'card-body bg-white'})
		data_list = data_soup.find('ul')
		items = data_list.find_all('li')
		for elem in items:
			if items.index(elem) == 0:
				total = elem.text[12:]
			elif items.index(elem) == 1:
				deaths = elem.text[13:]
			else:
				pass
		context = {
			'total':total,
			'deaths':deaths,
			'country':"United States",
			'all_countries':all_countries,
		}
		return render(request, 'country.html', context=context)
	else:
		response = requests.get(confirmed_url.format(country_name)).text
		confirmed = json.loads(response)
		response = requests.get(death_url.format(country_name)).text
		death = json.loads(response)
		context = {
			'total': confirmed[-1]['Cases'],
			'deaths': death[-1]['Cases'],
			'country': death[-1]['Country'],
			'all_countries':all_countries,
		}
		return render(request,'country.html', context=context)
