import os
import sys
import json
import shutil
import glob
import datetime

# ==========================================
# 設定
# ==========================================

# 言語指定
TARGET_EXTENSION = ".py" 

CPH_DIR = ".cph"
REFERENCE_FILE = "ref.py" 

# 除外ファイル
EXCLUDE_FILES = [
    "template.py",
    "ref.py"
]

# ヘッダーテンプレート
HEADER_TEMPLATE = """\"\"\"
Title:  {name}
URL:    {url}
Date:   {date}

Algorithm:
    None

Complexity:
    Time: O(N)
    Space: O(1)

Points:
\"\"\"
"""

def get_latest_target_file():
    files = glob.glob(f"*{TARGET_EXTENSION}")
    
    current_script = os.path.basename(__file__)
    exclude_list = EXCLUDE_FILES + [current_script]
    candidates = [f for f in files if f not in exclude_list]

    if not candidates:
        return None
    
    candidates.sort(key=os.path.getmtime, reverse=True)
    return candidates[0]

def get_cph_info(target_file):
    info = {"path": None, "url": "", "name": "", "input": "", "output": ""}

    if not os.path.exists(CPH_DIR):
        return info

    for filename in os.listdir(CPH_DIR):
        if not (filename.endswith('.prob') or filename.endswith('.json')):
            continue
            
        json_path = os.path.join(CPH_DIR, filename)
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            src_path = data.get("srcPath", "").replace("\\", "/")
            
            if src_path.endswith(target_file):
                info["path"] = json_path
                info["url"] = data.get("url", "")
                info["name"] = data.get("name", "")
                
                tests = data.get("tests", [])
                if tests:
                    info["input"] = tests[0].get("input", "")
                    info["output"] = tests[0].get("output", "")
                return info
        except Exception:
            continue
            
    return info

def add_header(target_file, problem_name, problem_url):
    if not problem_url:
        return

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "Title:" not in content:
            header_text = HEADER_TEMPLATE.format(
                name=problem_name,
                url=problem_url,
                date=datetime.date.today().strftime('%Y-%m-%d')
            )
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(header_text + content)
            print(f"Update: ヘッダーを追記しました -> {target_file}")
            
    except Exception as e:
        print(f"Warning: ヘッダー追記に失敗しました: {e}")

def main():
    if len(sys.argv) != 2:
        print(f"使い方: python {os.path.basename(__file__)} <dest_folder>")
        return

    dest_root = sys.argv[1]

    target_file = get_latest_target_file()
    if not target_file:
        print(f"Error: {TARGET_EXTENSION} ファイルが見つかりません。")
        return

    print(f"Target: {target_file}")

    info = get_cph_info(target_file)
    add_header(target_file, info["name"], info["url"])

    try:
        folder_name = os.path.splitext(os.path.basename(target_file))[0]
        final_dest = os.path.join(dest_root, folder_name)
        
        os.makedirs(final_dest, exist_ok=True)

        with open(os.path.join(final_dest, "input.txt"), "w", encoding="utf-8") as f:
            f.write(info["input"])
        with open(os.path.join(final_dest, "output.txt"), "w", encoding="utf-8") as f:
            f.write(info["output"])

        shutil.move(target_file, os.path.join(final_dest, os.path.basename(target_file)))
        
        if os.path.exists(REFERENCE_FILE):
            new_ref_name = f"{folder_name}_reference{TARGET_EXTENSION}"
            shutil.move(REFERENCE_FILE, os.path.join(final_dest, new_ref_name))

        if info["path"] and os.path.exists(info["path"]):
            os.remove(info["path"])

        print(f"Success: アーカイブ完了 -> {final_dest}")

    except Exception as e:
        print(f"Error: 予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    main()