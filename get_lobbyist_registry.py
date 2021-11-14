import requests
import csv
import datetime
from bs4 import BeautifulSoup
import re


def getRegistry():
	pageCounter = 0
	records = []
	while checkForResults("https://www.hamilton.ca/government-information/accountability/lobbyist-registry/search?page=" + str(pageCounter)):
		print("Page " + str(pageCounter) + " contains results! \n")
		detailsURLs = parseResults("https://www.hamilton.ca/government-information/accountability/lobbyist-registry/search?page=" + str(pageCounter))
		pageCounter += 1
		for detailsURL in detailsURLs:
			print("Details URL: " + detailsURL)
			record = parseDetails(detailsURL)
			print("Record: " + str(record) + "\n")
			records.append(record)
	writeRecords(records)


def fetch(url):
	return(requests.get(url).text)


def checkForResults(url):
	resultsPage = BeautifulSoup(fetch(url), "html.parser")
	if resultsPage.find_all(class_="view-content"):
		return True


def parseResults(url):
	resultsPage = BeautifulSoup(fetch(url), "html.parser")
	detailsURLs = []
	for row in resultsPage.tbody.find_all('tr'):
		detailsURLs.append("https://www.hamilton.ca" + str(row.td.a['href']))
	return detailsURLs


def parseDetails(url):
	detailsPage = BeautifulSoup(fetch(url), "html.parser")
	record = {}

# Add name to record
	if detailsPage.find(id="mini-panel-lobbyist_profile_for_sm"):
		record['name'] = detailsPage.find(id="mini-panel-lobbyist_profile_for_sm").div.div.div.div.contents[0].strip()
	elif detailsPage.find(id="mini-panel-subject_matter_summary"):
		record['name'] = detailsPage.find(id="mini-panel-subject_matter_summary").div.div.div.div.strong.contents[0].strip()

# Add title to record
	if detailsPage.find(class_="field field--name-field-position field--type-text field--label-hidden"):
		record['title'] = detailsPage.find(class_="field field--name-field-position field--type-text field--label-hidden").div.div.contents[0].strip()
	else:
		record['title'] = ""

# Add lobbyist type to record
	record['lobbyist_type'] = detailsPage.find(class_="field field--name-field-lobbyist-type field--type-entityreference field--label-inline clearfix").find_all('div')[2].contents[0].strip()

# Add client to record
	if detailsPage.find(class_="field field--name-field-business-name field--type-text field--label-hidden").div.div.find(class_="__cf_email__"):
		record['client'] = ""
	else:
		record['client'] = detailsPage.find(class_="field field--name-field-business-name field--type-text field--label-hidden").div.div.contents[0].strip()

# Add lobbyist status to record
	if detailsPage.find(class_="field field--name-field-lobbyist-status field--type-workflow field--label-inline clearfix"):
		record['lobbyist_status'] = detailsPage.find(class_="field field--name-field-lobbyist-status field--type-workflow field--label-inline clearfix").find_all('div')[2].contents[0].strip()
	else:
		record['lobbyist_status'] = ""

# Add start_date to record
	record['start_date'] = detailsPage.find(class_="field field--name-field-lobbying-start field--type-datestamp field--label-inline clearfix").find_all('div')[2].span.contents[0].strip()

# Add end_date to record
	record['end_date'] = detailsPage.find(class_="field field--name-field-lobbying-end field--type-datestamp field--label-inline clearfix").find_all('div')[2].span.contents[0].strip()

# Add street addresses to record
	# If there is more than one street address
	if len(detailsPage.find_all(class_="adr")) > 1:
		# Add the first one to the record as lobbyist_street_address_1
		record['lobbyist_street_address_1'] = detailsPage.find_all(class_="adr")[0].find(itemprop="streetAddress").contents[0].strip()
		# And if there is an additional field for that address, add it as lobbyist_street_address_2
		if len(detailsPage.find_all(class_="adr")[0].find_all(itemprop="streetAddress")) > 1:
			record['lobbyist_street_address_2'] = detailsPage.find_all(class_="adr")[0].find_all(itemprop="streetAddress")[1].contents[0].strip()
		# Add the postal code, city, region and country
		record['lobbyist_postal_code'] = detailsPage.find_all(class_="adr")[0].find(class_="postal-code").contents[0].strip()
		record['lobbyist_city'] = detailsPage.find_all(class_="adr")[0].find(class_="locality").contents[0].strip()
		record['lobbyist_region'] = detailsPage.find_all(class_="adr")[0].find(class_="region").contents[0].strip()
		record['lobbyist_country'] = detailsPage.find_all(class_="adr")[0].find(class_="country-name").contents[0].strip()
		# Add the second one to the record as client_streetaddress_1
		record['client_street_address_1'] = detailsPage.find_all(class_="adr")[1].find(itemprop="streetAddress").contents[0].strip()
		# And if there is an additional field for that address, add it as client_street_address_2
		if len(detailsPage.find_all(class_="adr")[1].find_all(itemprop="streetAddress")) > 1:
			record['client_street_address_2'] = detailsPage.find_all(class_="adr")[1].find_all(itemprop="streetAddress")[1].contents[0].strip()
		# Add the postal code, city, region and country
		record['client_postal_code'] = detailsPage.find_all(class_="adr")[1].find(class_="postal-code").contents[0].strip()
		record['client_city'] = detailsPage.find_all(class_="adr")[1].find(class_="locality").contents[0].strip()
		record['client_region'] = detailsPage.find_all(class_="adr")[1].find(class_="region").contents[0].strip()
		record['client_country'] = detailsPage.find_all(class_="adr")[1].find(class_="country-name").contents[0].strip()
	# If there's only one street address
	else:
		# Leave the lobbyist street address empty
		record['lobbyist_street_address_1'] = ""
		# And add the address as the client_street_address_1
		record['client_street_address_1'] = detailsPage.find(class_="adr").find(itemprop="streetAddress").contents[0].strip()
		# And if there is an additional field for that address, add it as lobbyist_street_address_2
		if len(detailsPage.find(class_="adr").find_all(itemprop="streetAddress")) > 1:
			record['lobbyist_street_address_2'] = detailsPage.find(class_="adr").find_all(itemprop="streetAddress")[1].contents[0].strip()
		# Add the postal code, city, region and country
		record['client_postal_code'] = detailsPage.find(class_="adr").find(class_="postal-code").contents[0].strip()
		record['client_city'] = detailsPage.find(class_="adr").find(class_="locality").contents[0].strip()
		record['client_region'] = detailsPage.find(class_="adr").find(class_="region").contents[0].strip()
		record['client_country'] = detailsPage.find(class_="adr").find(class_="country-name").contents[0].strip()

# Add subject matter category to record
	record['subject_matter_category'] = detailsPage.find(class_="field field--name-field-subject-matter-category field--type-entityreference field--label-inline clearfix").find(class_="field__items").div.contents[0].strip()

# Add subject status to record
	record['subject_matter_status'] = detailsPage.find(class_="field field--name-field-subject-matter-status field--type-workflow field--label-inline clearfix").find(class_="field__items").div.contents[0].strip()

#Add activity description to record
	record['activity_description'] = detailsPage.find(class_="field field--name-body field--type-text-with-summary field--label-inline clearfix").find(class_="field__items").div.contents[0].strip()

#Add public office holders to record
	public_office_holders = []
	for div in detailsPage.find(class_="field field--name-field-lobbied-official field--type-entityreference field--label-inline clearfix").find(class_="field__items"):
		poh_list = re.split("\s[-]\s", (div.contents[0]))
		public_office_holder = {}
		public_office_holder["name"] = poh_list[0]
		public_office_holder["title"] = poh_list[1]
		public_office_holders.append(public_office_holder)
	record['public_office_holders'] = public_office_holders

	# print(record)
	return(record)


def writeRecords(records):
	fieldnames = ['name',
	'title',
	'lobbyist_type',
	'client',
	'lobbyist_status',
	'start_date',
	'end_date',
	'lobbyist_street_address_1',
	'lobbyist_street_address_2',
	'lobbyist_city',
	'lobbyist_region',
	'lobbyist_country',
	'lobbyist_postal_code',
	'client_street_address_1',
	'client_street_address_2',
	'client_city',
	'client_region',
	'client_country',
	'client_postal_code',
	'subject_matter_category',
	'subject_matter_status',
	'activity_description',
	'public_office_holders']
	current_date = datetime.datetime.now()
	csvfile = open('hamilton_lobbyist_registry_'+str(current_date.month)+'-'+str(current_date.day)+'-'+str(current_date.year)+'.csv', 'w', encoding='utf8', newline='')	
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	for r in records:
		writer.writerow(r)
	csvfile.close()

getRegistry()

# parseDetails("https://www.hamilton.ca/subject-matter/john-matheson-behalf-jim-hadjiyianni-lobbying-smith-janette-city-manager")