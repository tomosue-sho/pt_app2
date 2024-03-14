import json

def find_duplicates(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    entries = {}
    duplicates = []

    for item in data:
        key = (item.get('app_label'), item.get('model'))
        if key in entries:
            duplicates.append(key)
        else:
            entries[key] = True

    return duplicates

if __name__ == "__main__":
    json_file = '/Users/tomosue_shou/mysite/datadump.json'
    duplicates = find_duplicates(json_file)
    if duplicates:
        print("重複エントリが見つかりました:")
        for entry in duplicates:
            print(entry)
    else:
        print("重複エントリは見つかりませんでした。")
