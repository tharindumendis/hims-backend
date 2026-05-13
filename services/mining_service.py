import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from database import get_db_pool

def get_association_rules(min_support=0.05, min_confidence=0.3):
    pool = get_db_pool()
    query = """
        SELECT prescription_id, medicine_name
        FROM vw_patient_prescription_history
    """
    try:
        rows = pool.execute_query(query)
        if not rows:
            return []
        
        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=['prescription_id', 'medicine_name'])
        
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
    query = """
        SELECT
          m.medicine_name,
          EXTRACT(YEAR FROM t.txn_date) AS yr,
          EXTRACT(MONTH FROM t.txn_date) AS mo,
          SUM(t.quantity) AS total_consumed
        FROM STOCK_TRANSACTION t
        JOIN MEDICINE m ON t.medicine_id = m.medicine_id
        WHERE t.txn_type = 'OUT'
        GROUP BY m.medicine_name, EXTRACT(YEAR FROM t.txn_date), EXTRACT(MONTH FROM t.txn_date)
        ORDER BY yr, mo, m.medicine_name
    """
    try:
        rows = pool.execute_query(query)
        results = []
        for row in rows:
            results.append({
                "medicine_name": row[0],
                "year": int(row[1]),
                "month": int(row[2]),
                "total_consumed": int(row[3])
            })
        return results
    except Exception as e:
        print(f"Error in trend: {e}")
        return []
