from flask import Response
import json
import yaml
import xml.etree.ElementTree as ET

def serialize_json(data):
    return Response(
        json.dumps(data, ensure_ascii=False),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=data.json"}
    )

def serialize_yaml(data):
    return Response(
        yaml.dump(data, allow_unicode=True),
        mimetype="application/x-yaml",
        headers={"Content-Disposition": "attachment; filename=data.yaml"}
    )

def serialize_xml(data, root_tag="dataset", record_tag="record", value_field=None):
    root = ET.Element(root_tag)
    for record in data:
        elem = ET.SubElement(root, record_tag)
        elem.set("date", str(record["date"]))
        elem.text = str(record.get(value_field, ""))
    xml_str = ET.tostring(root, encoding="utf-8")
    return Response(
        xml_str,
        mimetype="application/xml",
        headers={"Content-Disposition": "attachment; filename=data.xml"}
    )
