import pickle

base_pre = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>All rC3 maps</title>
<style>
table {
      font-family: arial, sans-serif;
        border-collapse: collapse;
          width: 100%;
}

    td, th {
          border: 1px solid #dddddd;
            text-align: left;
              padding: 8px;
    }

    tr:nth-child(even) {
          background-color: #dddddd;
    }
</style>
</head>
<body>
<div>
    <h1><a>All rC3 maps</a></h1>
</div>
<table style="width:100%">
    <tr>
        <th>Exit Metadata</th>
        <th>Link (may be on strange instance)</th>
    </tr>
    <tr>"""

base_post = """
</table>
</body>
</html>
"""
print(base_pre)
file = "2020-12-27_23-01-13_finished_iter_8.pkl"
data = pickle.load(open(file, "rb"))
pre="https://visit.at.rc3.world/as/flauschiversum/r91kY7sQicjviPmpGunqjM/_/global/"
for d in data["data"]:
    a = d[1].replace('https://', '')
    print(f"""    <tr>
        <th>{d[0]}</th>
        <th> <a href={pre + a} </a>{a}</th>
<tr>""")

print(base_post)