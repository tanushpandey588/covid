import pandas as pd
import numpy as np

np.random.seed(42)

countries = [
    "India","USA","Brazil","Russia","France","Germany","Italy",
    "United Kingdom","Spain","Canada","Australia","Japan",
    "China","Mexico","South Africa","Argentina","Indonesia",
    "Pakistan","Bangladesh","Turkey"
]

continents = {
    "India":"Asia",
    "USA":"North America",
    "Brazil":"South America",
    "Russia":"Europe",
    "France":"Europe",
    "Germany":"Europe",
    "Italy":"Europe",
    "United Kingdom":"Europe",
    "Spain":"Europe",
    "Canada":"North America",
    "Australia":"Australia",
    "Japan":"Asia",
    "China":"Asia",
    "Mexico":"North America",
    "South Africa":"Africa",
    "Argentina":"South America",
    "Indonesia":"Asia",
    "Pakistan":"Asia",
    "Bangladesh":"Asia",
    "Turkey":"Europe"
}

dates = pd.date_range("2020-01-01","2022-01-20")

rows = []

for country in countries:

    population = np.random.randint(5_000_000,1_500_000_000)

    total_cases = 0
    total_deaths = 0
    total_recovered = 0
    total_vaccinated = 0

    for date in dates:

        new_cases = max(0,int(np.random.normal(1200,450)))
        new_deaths = max(0,int(new_cases*np.random.uniform(0.01,0.04)))
        new_recovered = max(0,int(new_cases*np.random.uniform(0.75,0.97)))
        new_vaccinations = max(0,int(np.random.normal(5000,1800)))

        total_cases += new_cases
        total_deaths += new_deaths
        total_recovered += new_recovered
        total_vaccinated += new_vaccinations

        active_cases = total_cases-total_recovered-total_deaths

        tests = new_cases*np.random.randint(8,20)

        if tests == 0:
            positivity_rate = 0
        else:
            positivity_rate = round((new_cases / tests) * 100, 2)
        recovery_rate = round((total_recovered/max(total_cases,1))*100,2)

        death_rate = round((total_deaths/max(total_cases,1))*100,2)

        vaccination_rate = round((total_vaccinated/population)*100,2)

        hospital_patients = np.random.randint(50,5000)

        icu_patients = np.random.randint(10,800)

        new_tests = tests

        total_tests = tests*np.random.randint(100,400)

        rows.append({

            "Date":date,

            "Country":country,

            "Continent":continents[country],

            "Population":population,

            "New_Cases":new_cases,

            "Total_Cases":total_cases,

            "New_Deaths":new_deaths,

            "Total_Deaths":total_deaths,

            "New_Recovered":new_recovered,

            "Total_Recovered":total_recovered,

            "Active_Cases":active_cases,

            "New_Vaccinations":new_vaccinations,

            "Total_Vaccinations":total_vaccinated,

            "Vaccination_Rate":vaccination_rate,

            "New_Tests":new_tests,

            "Total_Tests":total_tests,

            "Hospital_Patients":hospital_patients,

            "ICU_Patients":icu_patients,

            "Positivity_Rate":positivity_rate,

            "Recovery_Rate":recovery_rate,

            "Death_Rate":death_rate

        })

df = pd.DataFrame(rows)

# Add some missing values intentionally for EDA practice

for col in ["Hospital_Patients","ICU_Patients","Vaccination_Rate"]:
    df.loc[df.sample(frac=0.02).index,col] = np.nan

df.to_csv("covid19_newdataset.csv",index=False)

print("CSV Generated Successfully")
print(df.head())

print("\nShape:",df.shape)