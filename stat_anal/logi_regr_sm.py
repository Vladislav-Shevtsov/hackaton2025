import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, roc_auc_score
import forestplot as fp
import statsmodels.api as sm

num = ["age", "hla", "NC", "CD34"]
#date_hsct, status_before_hsct


nom = ["ds_clear", "gender", "Prof", "origin", "RIC_MAC.x", "hsct_type"]

labels = ["id", "ds_clear", "age", 
    "gender", "hla", "Prof", "RIC_MAC.x", "hsct_type", "origin", "date_hsct", 
    "status_before_hsct", "NC", "CD34", "CD3", "tma_date"]
df = pd.read_excel("Data/Ready/ready_characteritstics.xlsx", usecols=labels)


#df["date_hsct"] = df["tma_date"]-df["date_hsct"]
df["RIC_MAC.x"] = df["RIC_MAC.x"].map({"RIC": 0, "MAC": 1})
df["hsct_type"] = df["hsct_type"].map({"MRD": 0, "MUD": 1, "MMUD": 2, "HID": 3})
df["Prof"] = df["Prof"].str.replace(r'(CsaMTX)|(CsaMtx)|(HID_M)', "Other", regex=True)
#df["status_before_hsct"] = np.where(df["status_before_hsct"]=="Rem" or
#                                    df["status_before_hsct"].isna(), 'Rem', 'AD')

df["tma_date"] = np.where(df["tma_date"].isna(), 0, 1)



def logi_r(x, y):
    if x.shape[1] > 1:
        x = sm.add_constant(x)
    try:
        res = sm.Logit(y, x).fit(maxiter=300, disp=0)
        odds_ratios = np.exp(res.params)
        conf = pd.DataFrame(res.conf_int())
        conf['Odds Ratio'] = res.params
        conf.columns = ['5%', '95%', 'Odds Ratio']
        print(np.exp(conf))
    except np.linalg.LinAlgError:
        print("Singular matrix: cannot compute confidence intervals for this variable.")


def cat(df, c):
    y = np.array(df["tma_date"])
    x = pd.get_dummies(df[c], drop_first=True, dtype=float)
    x = x.loc[:, x.nunique() > 1]
    print(x.columns)
    return x, y


for c in nom:
    print(f"{c}: {df[c].unique()} (n_unique={df[c].nunique()})")
    x, y = cat(df, c)
    logi_r(x, y)


for c in num:
    print(c)
    x = np.array(df[c]).reshape(-1,1)
    y = np.array(df["tma_date"])
    mask = (~np.isnan(x).flatten()) & (~pd.isna(y))
    x = x[mask]
    y = y[mask]
    logi_r(x, y)
