# === File: commerce_etl/validators.py ===
from commerce_etl.config import CURRENCY_RATES, BLACKLIST_USERS, VALID_STATUSES, VIP_THRESHOLD

# Định nghĩa hàm xác nhận chuỗi nguyên dương
def is_positive_number(raw_str):
    if raw_str.strip().isdigit() and int(raw_str.strip()) > 0:
        return True
    return False


# Định nghĩa hàm has_required_fields
def has_required_fields(record, *required_cols):
    for col_name in required_cols:
        val = record.get(col_name.strip(), None)
        if val is None or str(val).strip() == '':
            return False
    return True


# Định nghĩa hàm is_valid_transastion
def is_valid_transaction(tx_dict):
    # Gọi hàm kiểm tra các trường
    if has_required_fields(tx_dict, "tx_id", "user_id", "amount_str", "currency", "status"):
        if tx_dict['user_id'].strip().upper() not in BLACKLIST_USERS and tx_dict['status'].strip().upper() in VALID_STATUSES and is_positive_number(tx_dict['amount_str'].strip()):
            return True
        return False
    return False


if __name__ == "__main__":
    print(is_positive_number(' 56 '))
    print(has_required_fields({'tx_id': 'TX_107 ', 'user_id': ' USR_02 ', 'amount_str': ' 60 ', 'currency': ' USD ', 'status': ' SUCCESS'}, "tx_id", "user_id", "amount_str", "currency", "status"))
    