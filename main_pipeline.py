# === File: main_etl.py ===
from commerce_etl.transformers import parse_raw_line, transform_transaction, rank_transactions
from commerce_etl.load_export_data import read_existing_dw_tx_ids, read_txt_file, load_to_json

# Hàm run_pipline
def run_pipeline(raw_logs, existing_dw_ids=None, batch_id="BATCH_01"):
    if existing_dw_ids is None:
        existing_dw_ids = set()
    
    seen_batch_ids = set()
    clean_batch_records = []
    rejected_count = 0

    for log in raw_logs:
        parsed_log = parse_raw_line(log)
        if not parsed_log:
            rejected_count += 1
            continue

        normalized_id = parsed_log['tx_id'].strip().upper()
        if normalized_id in seen_batch_ids:
            rejected_count += 1
            continue

        transformed_tx = transform_transaction(
           parsed_log,
           batch_id=batch_id,
           pipeline='COMMERCE_CORE'
        )
        if transformed_tx is not None:
            seen_batch_ids.add(normalized_id)
            clean_batch_records.append(transformed_tx)
        else: 
            rejected_count += 1
    

    new_tx_ids = seen_batch_ids - existing_dw_ids
    records_to_load = [record for record in clean_batch_records if record['tx_id'] in new_tx_ids]
    dw_duplicate_count = len(seen_batch_ids) - len(records_to_load)

    # Trả về kết quả
    return (records_to_load, rejected_count, dw_duplicate_count)


# Hàm sumamrize
def summarize_by_user(records):
    total_amount_by_user = {}
    for record in records:
        user_id = record['user_id']
        total_amount_by_user[user_id] = record['vnd_amount'] + total_amount_by_user.get(user_id, 0)
    return total_amount_by_user

if __name__ == "__main__":
    RAW_LOGS = read_txt_file(r'data\raw_data\raw_log.txt')

    EXISTING_DW_TX_IDS = read_existing_dw_tx_ids(r'data\processed_data\existing_dw_tx_ids.txt')

    records_to_load, rejceted_count, existing_dw_count = run_pipeline(RAW_LOGS, EXISTING_DW_TX_IDS)
    total_amount_by_user = summarize_by_user(records_to_load)

    # Ghi dữ liệu cần load lên server ra file json
    load_to_json(records_to_load, r'data\processed_data\data_to_load.json')

    # Print Final Result
    print(f"- Số giao dịch hợp lệ nạp và DW là: {len(records_to_load)} giao dịch, thông tin các giao dịch được ghi vào file json: data\processed_data\data_to_load.json")
    print(f"- Số giao dịch bị loại bỏ là: {rejceted_count} giao dịch")
    print(f"- Số giao dịch bị trùng (đã tồn tại trong DW) là: {existing_dw_count} giao dịch")
    print(f"===== BẢNG XẾP HẠNG GIAO DỊCH =====")
    print(rank_transactions(records_to_load, 5))
    print(f"===== TỔNG DOANH THU THEO TỪNG USER =====")
    print(total_amount_by_user)
    print("===== GIAO DỊCH CÓ GIÁ TRỊ LỚN NHẤT ======")
    max_transaction = max(
        records_to_load,
        key= lambda record: record['vnd_amount'], default=None
    )
    print(max_transaction)
