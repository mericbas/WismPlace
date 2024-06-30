from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# Excel dosya yolları
excel_files = {
    'yemek': 'data/yemek.xlsx',
    'tatli': 'data/tatli.xlsx',
    'pub': 'data/pub.xlsx',
    'diger': 'data/diger.xlsx',

    'yemek_readonly': 'data/yemek.xlsx',
    'tatli_readonly': 'data/tatli.xlsx',
    'pub_readonly': 'data/pub.xlsx',
    'diger_readonly': 'data/diger.xlsx'
}

# Boş bir Excel dosyası şablonu
def create_empty_excel(file_path):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=['ID', 'Adı', 'Puan', 'Açıklama', 'Yer'])  # Kategori yerine Puan
        df.to_excel(file_path, index=False)
        print(f'{file_path} oluşturuldu.')

# Uygulama başlatıldığında gerekli dosyaları oluştur
def ensure_excel_files():
    os.makedirs('data', exist_ok=True)
    for file_path in excel_files.values():
        create_empty_excel(file_path)

ensure_excel_files()

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Dinamik sayfa yönlendirmesi
@app.route('/<category>', methods=['GET', 'POST'])
def category_page(category):
    if category.endswith('_readonly'):
        return handle_page(category, readonly=True)

    if category == 'back':
        return render_template('duzenlenir.html')

    if category == 'backO':
        return render_template('okunur.html')

    if category == 'okunur':
        return render_template('okunur.html')

    if category == 'main':
        return render_template('index.html')
    if category == 'duzenlenir':
        return render_template('duzenlenir.html')
    if category not in excel_files:
        return redirect(url_for('index'))

    return handle_page(category)

def handle_page(category, readonly=False):
    excel_file = excel_files.get(category)
    if not excel_file:
        print(f"Error: No excel file found for category '{category}'")
        return "Error: No excel file found for category"

    if request.method == 'POST':
        if 'delete' in request.form:
            delete_rows(request.form.getlist('selected'), excel_file)
        elif 'add' in request.form:
            add_row(request.form, excel_file)
        elif 'save' in request.form:
            save_data(request.form, excel_file)
        elif 'main' in request.form:
            return render_template('okunur.html' if readonly else 'duzenlenir.html')

    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"Error reading excel file: {e}")
        return f"Error reading excel file: {e}"

    if df.empty:
        print("DataFrame is empty")
        data = []
    else:
        data = [{'index': idx, **row} for idx, row in df.iterrows()]
        print("Data loaded successfully:", data)

    template_name = f'{category}.html' if readonly else f'{category}.html'
    print(f"Using template: {template_name}")
    return render_template(template_name, data=data, category=category)

def delete_rows(rows, excel_file):
    df = pd.read_excel(excel_file)
    indices = [int(row) for row in rows]
    df = df.drop(indices).reset_index(drop=True)
    df.to_excel(excel_file, index=False)

def add_row(form, excel_file):
    df = pd.read_excel(excel_file)
    new_row = {col: form.get(col, '') for col in df.columns}
    new_row['ID'] = df['ID'].max() + 1 if not df.empty else 1
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(excel_file, index=False)

def save_data(form, excel_file):
    try:
        df = pd.read_excel(excel_file)
        for idx, row in df.iterrows():
            for col in df.columns:
                key = f'{idx}-{col}'
                if key in form:
                    df.at[idx, col] = form[key]
        df.to_excel(excel_file, index=False)
    except Exception as e:
        print(f"Error saving data: {e}")
        return f"Error saving data: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
