import scrapers.elvasjutisju as elvasjutisju

search_results = elvasjutisju.get_vaccination_centers()

#for search_result in search_results:

elvasjutisju.get_covid_vaccination_link(
    '/hitta-vard/kontaktkort/Borgholms-halsocentral/')
