from flask import Flask, request, render_template, redirect, url_for, session, flash, send_file
import pandas as pd
import re
import io
##
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 운영환경에서는 안전한 값으로 변경하세요1

# 업로드한 엑셀 데이터를 저장할 전역 변수 (실제 서비스에서는 DB나 세션 관리가 필요함)
excel_data = []

@app.route("/", methods=["GET", "POST"])
def upload():
    global excel_data
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            try:
                df = pd.read_excel(file)
            except Exception as e:
                flash("엑셀 파일을 읽는 중 오류가 발생했습니다.")
                return redirect(url_for("upload"))
            # 반드시 Origin과 Translation 열이 존재해야 함
            if "Origin" not in df.columns or "Translation" not in df.columns:
                flash("엑셀 파일에는 'Origin'과 'Translation' 열이 있어야 합니다.")
                return redirect(url_for("upload"))
            excel_data = df.to_dict(orient="records")
            # 각 행의 원문과 번역을 문장 단위로 분리
            for row in excel_data:
                row["origin_sentences"] = re.split(r'(?<=[.!?])\s+', row["Origin"].strip())
                row["translation_sentences"] = re.split(r'(?<=[.!?])\s+', row["Translation"].strip())
            session["current_index"] = 0
            return redirect(url_for("proofread"))
    return render_template("upload.html")

@app.route("/proofread", methods=["GET", "POST"])
def proofread():
    global excel_data
    index = session.get("current_index", 0)
    # 검수할 행이 없는 경우 완료 페이지로 이동
    if index >= len(excel_data):
        return redirect(url_for("finish"))
    row = excel_data[index]
    if request.method == "POST":
        updated_sentences = []
        # 원문과 번역 중 더 많은 문장 수에 맞춰 처리
        num_sentences = max(len(row.get("origin_sentences", [])), len(row.get("translation_sentences", [])))
        for i in range(num_sentences):
            updated_sentence = request.form.get(f"sentence_{i}", "").strip()
            updated_sentences.append(updated_sentence)
        # 수정된 문장들 중 빈 문자열은 제외하고 재조합
        row["translation_sentences"] = updated_sentences
        row["Translation"] = " ".join([s for s in updated_sentences if s])
        excel_data[index] = row

        action = request.form.get("action")
        # '저장' 버튼을 누르면 남은 행은 건너뛰고 바로 완료 페이지로 이동
        if action == "저장":
            return redirect(url_for("finish"))
        else:
            session["current_index"] = index + 1
            if session["current_index"] >= len(excel_data):
                return redirect(url_for("finish"))
            else:
                return redirect(url_for("proofread"))
    return render_template("proofread.html", row=row, index=index, total=len(excel_data))

@app.route("/finish")
def finish():
    return render_template("finish.html", total=len(excel_data))

@app.route("/download")
def download():
    global excel_data
    df = pd.DataFrame(excel_data)
    # 임시로 생성한 helper 열은 제거
    if "origin_sentences" in df.columns:
        df = df.drop(columns=["origin_sentences", "translation_sentences"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="updated.xlsx")

if __name__ == '__main__':
    app.run(debug=True)
