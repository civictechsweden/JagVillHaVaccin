# Jag Vill Ha Vaccin! 💉

**Jag Vill Ha Vaccin! is still a really early prototype. Don't expect it to find all the vaccination centers nor all the doses!**

**ACCESS THE (VERY EARLY) PROTOTYPE AT [jagvillhavaccin.nu](https://jagvillhavaccin.nu)**

**Jag Vill Ha Vaccin!** (*I want a vaccine!* in English or *Je veux un vaccin !* in French) is a project to harvest vaccination times throughout Sweden and display them in a user-friendly way.

The goal of the project is to make it easier for citizens who are looking for a dose, especially the most vulnerable who are often the ones struggling to understand the mess of websites and booking platforms, to help Swedish regions with their campaigns as they scale up and to act as a buffer between the enormous demand and booking platforms.

In short, **Jag Vill Ha Vaccin!** aims at saving lives by making sure every dose gets used as quickly and as fairly as possible.

## Roadmap 🗺

### Scraping ⚙️

Currently, the project is scraping data from the booking platform **mittvaccin.se** and **vaccina.se**. It does so regularly through a Github Action.

These services are used by some or all vaccination centers in the Blekinge, Jönköping, Kalmar, Kronoberg and Örebro.

#### Open booking platforms

A next goal is to scrape data from other platforms which don't require an authentification such as:
- patient.nu (WebDoc)
- Bokamera
- CGM J4

#### Official pages from regions

And from the pages of regions that already gather the information on user-friendly pages such as:
- Region VästraGötaland (kudos to [Marcus Österberg](https://github.com/marcusosterberg) and his team!)
- Region Västmanland
- Region Västerbotten

#### Closed platforms

Ideally, we would also want to get data from the platforms that require an authentification (often BankID) to see vaccination times. We'd love to get data from:
- 1177
- Alltid öppet
- Doktor.se
- Kry
- MittHalland (Region Halland)
- Plattform24.se (Region Gävleborg)

That requires a dialogue with them so if you know a relevant contact or are in charge of a region's booking system, reach out! These platforms are currently seeing 10s of thousands of visits daily (hourly) just to show the user that there are no available slots. Let's get them rid of that unneeded burden!

#### Other types of data

Finally, to support more advanced filtering functions, more metadata on vaccination centers, more metadata on the eligibility criteria (55+, risk group...) and some static geodata (postcodes) are needed.

As of now, the project is scraping metadata about vaccination centers from 1177.se.

### Frontend 🎨

The user interface is reusing the code from the French project Vite Ma Dose. Right now, some useful filtering functions have been disabled because they need to be adapted to the Swedish system.

The user interface should be as user-friendly as possible with possibility to filter doses by time (soonest) and place (close to me, in my municipality). If possible, by eligibility criteria (age, risk group...)

It also has to be static to make sure the project can scale up without experiencing the same bottlenecks as the official booking platforms

### I want to help! 🙋🏾‍♀️

Anyone is welcome to contribute to the project!

If you're a developer, you can help to build this website and the underlying scrapers.

Even if you can't code, there are probably many things you can help with! I recommend to check out Vite Ma Dose (see below), a French website with the same goal. The service is built by dozens of volunteers who also take care of its marketing, provide support and provides a valuable service to millions of people in France.

### I want to reuse! 👨🏼‍💻

As you probably noticed, the source code of this repository is open and you can reuse it as you wish according to the terms of the AGPL 3.0 license. The frontend of the tool is based on the French project Vite Ma Dose which uses the CC-BY-NC-SA license so our fork keeps the same license.

Attribution isn't mandatory but is greatly appreciated. As AGPL and CC-BY-NC-SA prescribe, you are required to publish the code of your own project if you wish to reuse it.

Regarding the data, it consists of public booking times that are scraped from private websites so I am unsure of the license that can be applied. I suggest ***CC-BY Jag Vill Ha Vaccin!***.

## Thank you ♥️

**Jag Vill Ha Vaccin!** is inspired of [Vite Ma Dose](http://vitemadose.covidtracker.fr), a French service built by [Guillaume Rozier](https://twitter.com/GuillaumeRozier) and many more.
