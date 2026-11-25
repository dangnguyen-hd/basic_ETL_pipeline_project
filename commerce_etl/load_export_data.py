import json

def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = []
            for line in f:
                data.append(line.strip('", \n'))
            f.close()
        return data
    except Exception as e:
        print(f"Có lỗi xảy ra! {e}")
        return []


def read_existing_dw_tx_ids(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = set()
            for line in f:
                data.add(line.strip())
            f.close()
        return data
    except Exception as e:
        print(f"Có lỗi xảy ra! {e}")
        return ""


def load_to_json(dict_records, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(dict_records, f, indent=4, ensure_ascii=False)
        f.close()
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

if __name__=="__main__":
    print(read_txt_file(r'data\raw_log.txt'))
    print(read_existing_dw_tx_ids(r'data\existing_dw_tx_ids.txt'))