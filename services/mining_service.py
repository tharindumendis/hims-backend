import pandas as pd
import oracledb
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from database import get_db_pool, fetch_data

def get_association_rules(min_support=0.05, min_confidence=0.3):
    pool = get_db_pool()
    try:
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            rows_dict = fetch_data(cursor, 'proc_get_apriori_data', [])
            
        if not rows_dict:
            return []
            
        # Convert dict list to DataFrame
        df = pd.DataFrame(rows_dict)
        
        baskets = df.groupby('prescription_id')['medicine_name'].apply(list).tolist()
        te = TransactionEncoder()
        te_array = te.fit_transform(baskets)
        df_enc = pd.DataFrame(te_array, columns=te.columns_)
        
        freq_items = apriori(df_enc, min_support=min_support, use_colnames=True)
        if freq_items.empty:
            return []
        
        rules = association_rules(freq_items, metric='confidence', min_threshold=min_confidence)
        rules_sorted = rules.sort_values('lift', ascending=False)
        
        results = []
        for _, row in rules_sorted.iterrows():
            results.append({
                "antecedents": list(row['antecedents']),
                "consequents": list(row['consequents']),
                "support": round(row['support'], 4),
                "confidence": round(row['confidence'], 4),
                "lift": round(row['lift'], 4)
            })
        return results
    except Exception as e:
        print(f"Error in Apriori: {e}")
        return []

def get_monthly_consumption_trend():
    pool = get_db_pool()
    try:
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            rows_dict = fetch_data(cursor, 'proc_get_monthly_trend', [])
            
        results = []
        for row in rows_dict:
            # Need to carefully handle datatypes since they might come as floats or strings
            results.append({
                "medicine_name": row["medicine_name"],
                "year": int(row["yr"]),
                "month": int(row["mo"]),
                "total_consumed": int(row["total_consumed"])
            })
        return results
    except Exception as e:
        print(f"Error in trend: {e}")
        return []
