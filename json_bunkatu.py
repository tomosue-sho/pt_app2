import json

# データダンプファイルのパス
input_file = 'datadump.json'
# 分割したファイルを保存するディレクトリ
output_dir = './splitted/'

# ファイルを読み込む
with open(input_file, 'r') as f:
    data = json.load(f)

# モデルごとにデータを分類する
data_by_model = {}
for item in data:
    model = item['model']
    if model not in data_by_model:
        data_by_model[model] = []
    data_by_model[model].append(item)

# モデルごとにファイルに書き出す
for model, items in data_by_model.items():
    filename = f"{output_dir}{model.replace('.', '_')}.json"
    with open(filename, 'w') as f:
        json.dump(items, f, indent=4)

print("分割完了")
