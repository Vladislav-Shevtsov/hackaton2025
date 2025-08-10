import pandas as pd

data = ["sch_alt_ast_bil_crea_urea_parsed.xlsx",
"coagulation_parsed.xlsx",
"crp_pct_ferritin_parsed.xlsx",
"kak_parsed.xlsx"]

out = []
for f in data:
    if f == "blood_viruses_parsed.xlsx" or f == "sch_alt_ast_bil_crea_urea_parsed.xlsx":
        df = pd.read_excel("./Data/Ready/"+f, usecols=["Рег.№", "Дата забора", "Синоним", "Результаты"])
        df.rename(columns={"Синоним" : "Test", "Результаты" : "Value"}, inplace=True)
        df["Value"] = df["Value"].str.replace(r'^\.', '', regex=True)
        #print(df.columns)
        
    else:
        df = pd.read_excel("./Data/Ready/"+f)
    df.rename(columns={"Рег.№" : "Reg.N", "Дата забора" : "Test_date"}, inplace=True)
    df = df.reindex(sorted(df.columns), axis=1)
    out.append(df)


out_df = pd.DataFrame(pd.concat(out))
#print(out_df.columns)
#print(out_df)

out_df.to_csv("./Data/Ready/all_anals.csv", index=False)
