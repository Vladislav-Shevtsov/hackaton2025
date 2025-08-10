import pandas as pd

fl = ("blood schisocytes.xlsx", "blood triglicerides.xlsx", "blood alt ast bil ldh.xlsx", "blood crea urea.xlsx", )

def filtr_df(file_name):
    df = pd.read_excel("./Data/"+file_name, usecols=["Рег.№", "Возр.", "Результаты", "Дата забора", "Синоним"])
    # ids = pd.read_excel("./Data/general diagnosis.xlsx", usecols=[0], chunksize=1000)
    df = df.dropna()
    df = df[df["Возр."].str.replace(r'[^0-9]', '', regex=True).astype(int) >= 18]
    #df = df[df["Дата ТКМ на дату выполнения услуги."] >= "2018-01-01"]
    #df = df.drop(["Возр.", "Дата ТКМ на дату выполнения услуги."], axis=1)
    #print(df.columns)

    df["Результаты"] = df["Результаты"].str.replace(r';.*', '', regex=True)
    df["Результаты"] = df["Результаты"].str.replace(r'[^0-9,\.]', '', regex=True)
    df = df[df["Результаты"] != '']
    df["Синоним"] = df["Синоним"].str.replace("шизоциты", "SHC")
    df["Синоним"] = df["Синоним"].str.replace("триглицериды", "TG")
    df["Синоним"] = df["Синоним"].str.replace('алт', "ALT")
    df["Синоним"] = df["Синоним"].str.replace('аст', "AST")
    df["Синоним"] = df["Синоним"].str.replace(r'.*билир.*', "BIL", regex=True)
    df["Синоним"] = df["Синоним"].str.replace('лдг', "LDH")
    df["Синоним"] = df["Синоним"].str.replace('креатинин', "CREA")
    df["Синоним"] = df["Синоним"].str.replace('мочевина', "URI")
    df.to_excel("./Data/Filtered/"+"filtered_"+file_name, index=False)
    return df

out = []
for f in fl:
    out.append(filtr_df(f))

conj_df = pd.DataFrame(pd.concat(out))
conj_df.to_excel("./Data/Filtered/united_filtered.xlsx", index=False, engine="openpyxl")
