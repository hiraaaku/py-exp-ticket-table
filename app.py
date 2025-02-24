from flask import Flask, render_template, request
import csv
from collections import defaultdict

app = Flask(__name__)

def load_data():
    data = defaultdict(lambda: {
        "Nama": "",
        "Bug Internal": 0,
        "Bug External": 0,
        "Total Bug": 0,
        "Support Internal": 0,
        "Support External": 0,
        "Total Support": 0,
        "IOW": 0,
        "Total": 0,
        "DocumentNo": set()
    })

    try:
        with open('data/data.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')

            for row in reader:
                assignee = row.get('Assignee', 'Unknown').strip()
                type_val = row.get('Type', '').strip()
                is_external = row.get('isExternal', '').strip()
                document_no = row.get('DocumentNo', '').strip()

                if not assignee:
                    continue
                
                data[assignee]["Nama"] = assignee
                
                if document_no:
                    data[assignee]["DocumentNo"].add(document_no)

                if type_val == "2":
                    if is_external == "No":
                        data[assignee]["Bug Internal"] += 1
                    elif is_external == "Yes":
                        data[assignee]["Bug External"] += 1
                
                elif type_val == "1":
                    if is_external == "No":
                        data[assignee]["Support Internal"] += 1
                    elif is_external == "Yes":
                        data[assignee]["Support External"] += 1
                
                elif type_val == "5":
                    data[assignee]["IOW"] += 1

            for assignee, values in data.items():
                values["Total Bug"] = values["Bug Internal"] + values["Bug External"]
                values["Total Support"] = values["Support Internal"] + values["Support External"]
                values["Total"] = values["Total Bug"] + values["Total Support"] + values["IOW"]
                values["DocumentNo"] = list(values["DocumentNo"])

        return list(data.values())
    except Exception as e:
        print("Error loading data:", e)
        return []

@app.route("/", methods=["GET"])
def index():
    data_records = load_data()
    project_filter = request.args.get("project", "").strip()
    department_filter = request.args.get("department", "").strip()

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    per_page = 10
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    if project_filter:
        data_records = [d for d in data_records if d.get("Project") == project_filter]
    if department_filter:
        data_records = [d for d in data_records if d.get("Department") == department_filter]

    paginated_data = data_records[start_idx:end_idx]
    total_pages = (len(data_records) + per_page - 1) // per_page

    return render_template("index.html", data=paginated_data, page=page, total_pages=total_pages)

if __name__ == "__main__":
    app.run(debug=True)
