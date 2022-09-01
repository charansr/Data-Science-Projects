import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mpld3

crime_data = pd.read_csv("/Users/charan/Documents/website/wages_vs_crime/state_crime.csv")
wage_data  = pd.read_csv("/Users/charan/Documents/website/wages_vs_crime/1929_2021_state_wage_2.csv")
inflation_data = pd.read_csv('/Users/charan/Documents/website/wage_v_inflation/Inflation(CPI)(7_21_22).csv')

def curate_wage_data(state):
    c_wage_data = wage_data[wage_data["GeoName"].str.contains(state)]
    c_wage_data = c_wage_data[c_wage_data["Description"].str.contains("Per capita personal income")]
    c_wage_data=c_wage_data.loc[0:]
    return c_wage_data

def curate_state_data(state):
    ac_state_data = crime_data[crime_data["State"].str.contains(state)]
    fc_state_data=pd.DataFrame()
    fc_state_data["Year"] = ac_state_data["Year"]
    fc_state_data["Values"] = ac_state_data["Data.Rates.Property.All"]+ac_state_data["Data.Rates.Violent.All"]
    fc_state_data.iloc[53,1]=np.nan
    fc_state_data.iloc[54,1]=np.nan
    fc_state_data.iloc[55,1]=np.nan
    fc_state_data["Values"] = fc_state_data["Values"].interpolate()
    #print(fc_state_data["Year"].isnull().values.any())
    fc_state_data["Year"]=[str(int(d)) for d in fc_state_data["Year"]]
    fc_state_data["Values"]=[int(d) for d in fc_state_data["Values"]]
    return fc_state_data

def curate_inflation_data(country):
    c_inflation_data = inflation_data[inflation_data["LOCATION"].str.endswith(country)]
    c_inflation_data = c_inflation_data[c_inflation_data["MEASURE"].str.endswith("IDX2015")]
    c_inflation_data = c_inflation_data[c_inflation_data["FREQUENCY"].str.endswith("A")]
    c_inflation_data = c_inflation_data[c_inflation_data["SUBJECT"].str.endswith("TOT")]
    return c_inflation_data

def graph_all(state):
    fig,ax = plt.subplots(figsize=(4,6))
    plt.style.use('fivethirtyeight')
    ###################
    ###crime vs time###
    ###################
    plt.subplot(3,1,1)
    c_crime_data=curate_state_data(state)
    c_wage_data=curate_wage_data(state)
    Xc = c_crime_data["Year"].values
    Yc = c_crime_data["Values"].values
    wtime = c_crime_data["Year"].values
    startpos=0
    istart = 1929
    wstart = int(wtime[0])
    if(istart>wstart):
        while(wstart<istart):
            startpos+=1
            wstart+=1
        Xc=Xc[startpos:]
        Yc=Yc[startpos:]
    Xcs=[str(int(d)) for d in Xc]
    Xcd=[pd.to_datetime(d) for d in Xcs]
    plt.xlabel("Year")
    plt.ylabel("Crimes per 100,000 people")
    plt.title("Crime Rate of "+state)
    plt.plot(Xcd,Yc)
    ###################
    ###wage vs time####
    ###################
    c_inflation_data=curate_inflation_data("USA")
    plt.subplot(3,1,2)
    Yg=[c_wage_data[str(d)] for d in Xc]
    c=0
    for i in Xc:
        a=c_inflation_data[c_inflation_data["TIME"].str.contains(str(i))]["Value"]
        a=float(a)
        Yg[c]=(Yg[c]/a)*100
        #print(Yg[c])
        c+=1
    plt.title("Average Wage per Capita in "+state)
    plt.ylabel("Pay in 2015 USD")
    plt.xlabel("Year")
    plt.plot(Xcd,Yg)
    ###################
    ###wage vs crime###
    ###################
    plt.subplot(3,1,3)
    plt.scatter(Yg,Yc)
    Yg=np.array(Yg)
    a=[]
    #print(Yg)
    for b in Yg:
        a.append(b[0])
    #print(a)
    coef = np.polyfit(a,Yc,1)
    poly1d_fn = np.poly1d(coef) 
    plt.plot(a,poly1d_fn(a),'--k')
    plt.xlabel("Wages in 2015 USD")
    plt.ylabel("Crimes per 100,000 people")
    plt.title("Wages vs Crime rate of "+state)
    plt.tight_layout(pad=0.1)
    #plt.show()
    html_str = mpld3.fig_to_html(fig)
    Html_file= open(state+".html","w")
    Html_file.write(html_str)
    Html_file.close()
    print("Correlation: " + str(np.corrcoef(a,Yc)[0,1]))

graph_all("United States")
