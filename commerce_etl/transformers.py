# === File: commerce_etl/transformers.py ===
from commerce_etl.config import CURRENCY_RATES, BLACKLIST_USERS, VALID_STATUSES, VIP_THRESHOLD
from commerce_etl.validators import is_valid_transaction, is_positive_number, has_required_fields

# Định nghĩa hàm tách dữ liệu
def parse_raw_line(raw_line):
    parts = raw_line.strip().split("|")
    if len(parts) != 5:
        return None

    tx_id, user_id, amount_str, currency, status = parts
    return {
        "tx_id": tx_id,
        "user_id": user_id, 
        "amount_str": amount_str, 
        "currency": currency, 
        "status": status
    }


# Định nghĩa hàm biến đổi dữ liệu giao dịch
def transform_transaction(tx_dict, default_currency="VND", **audit_tags):
    if not is_valid_transaction(tx_dict):
        return None

    # Chuẩn hóa
    tx_id = tx_dict['tx_id'].strip().upper()
    user_id = tx_dict['user_id'].strip().upper()
    currency = tx_dict['currency'].strip().upper() if tx_dict['currency'].strip().upper() else default_currency
    vnd_amount = int(int(tx_dict['amount_str'].strip()) * CURRENCY_RATES.get(currency, 1))
    tier = "VIP" if vnd_amount >= VIP_THRESHOLD else "STANDARD"
    processed_transaction = audit_tags.copy()
    processed_transaction.update({
        "tx_id": tx_id,
        'user_id': user_id,
        'vnd_amount': vnd_amount,
        'tier': tier,
        'status': tx_dict['status']
    })
    return processed_transaction


# Định nghĩa hàm rank_transactions
def rank_transactions(records, top_n=None):
    ranked_records = sorted(
        records,
        key= lambda record : (-record['vnd_amount'], record['tx_id'])
    )

    if top_n is not None:
        return ranked_records[:top_n]
    return ranked_records
    
