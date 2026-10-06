from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
from xml.sax.saxutils import escape


def formula_cell(ref, formula, style=None, num_format=None, is_string=False):
    attrs = f' r="{ref}"'
    if style:
        attrs += f' s="{style}"'
    if is_string:
        attrs += ' t="str"'
    out = [f'  <c{attrs}>']
    if formula:
        out.append(f'    <f>{escape(formula)}</f>')
    if is_string:
        out.append('    <v></v>')
    out.append('  </c>')
    return '\n'.join(out)


def value_cell(ref, value, style=None, cell_type=None):
    attrs = f' r="{ref}"'
    if style:
        attrs += f' s="{style}"'
    if cell_type:
        attrs += f' t="{cell_type}"'
    if isinstance(value, str):
        return f'  <c{attrs} t="inlineStr"><is><t>{escape(value)}</t></is></c>'
    return f'  <c{attrs}><v>{value}</v></c>'


def build_sheet1_xml():
    rows = []
    # A1:B11 input block
    values = {
        'A1': 'H [m]', 'B1': 4.0,
        'A2': 'gamma [kgf/m3]', 'B2': 18.0,
        'A3': 'phi [°]', 'B3': 30.0,
        'A4': 'c [kgf/m2]', 'B4': 0.0,
        'A5': 'delta [°]', 'B5': 0.0,
        'A6': 'beta [°]', 'B6': 0.0,
        'A7': 'alpha [°]', 'B7': 90.0,
        'A8': 'kh [g]', 'B8': 0.12,
        'A9': 'kv [g]', 'B9': 0.05,
        'A10': 'q [kgf/m2]', 'B10': 0.0,
        'A11': 'water_table [m]', 'B11': 0.0,
    }

    for row in range(1, 12):
        cells = []
        for col in ['A', 'B']:
            ref = f'{col}{row}'
            if ref in values:
                v = values[ref]
                if isinstance(v, str):
                    cells.append(value_cell(ref, v))
                else:
                    cells.append(value_cell(ref, v))
        rows.append('    <row r="%d">\n%s\n    </row>' % (row, '\n'.join(cells)))

    # Result cells block
    result_entries = [
        ('D1', 'theta [rad]', None, True),
        ('E1', None, 'ATAN(B8/(1-B9))', None, False),
        ('D2', 'theta [°]', None, True),
        ('E2', None, 'DEGREES(E1)', None, False),
        ('D3', 'gamma_eff', None, True),
        ('E3', None, 'B2*(1-B9)', None, False),
        ('D4', 'Kae', None, True),
        ('E4', None, '(COS(RADIANS(B3)+E1)^2)/ (COS(RADIANS(B7)+RADIANS(B5))^2 * COS(RADIANS(B6)-E1) * (1 + SQRT((SIN((RADIANS(B3)+E1)+(RADIANS(B7)+RADIANS(B5)))*SIN((RADIANS(B3)+E1)-(RADIANS(B6)-E1)))/(COS(RADIANS(B7)+RADIANS(B5))*COS(RADIANS(B6)-E1))))^2)', None, False),
        ('D5', 'Pa [kgf/m]', None, True),
        ('E5', None, 'SI(B11<B1;0.5*E3*B1^2*E4 + B10*B1*E4 - 2*B4*B1*RAIZ(E4) + 0.5*1000*(B1-B11)^2;0.5*E3*B1^2*E4 + B10*B1*E4 - 2*B4*B1*RAIZ(E4))', None, False),
        ('D6', 'Kpe', None, True),
        ('E6', None, '(COS(RADIANS(B3)+E1)^2)/ (COS(RADIANS(B7)-RADIANS(B5))^2 * COS(RADIANS(B6)+E1) * (1 - SQRT((SIN((RADIANS(B3)+E1)-(RADIANS(B7)-RADIANS(B5)))*SIN((RADIANS(B3)+E1)+(RADIANS(B6)+E1)))/(COS(RADIANS(B7)-RADIANS(B5))*COS(RADIANS(B6)+E1))))^2)', None, False),
        ('D7', 'Pp [kgf/m]', None, True),
        ('E7', None, 'SI(B11<B1;0.5*E3*B1^2*E6 + B10*B1*E6 + 2*B4*B1*RAIZ(E6) + 0.5*1000*(B1-B11)^2;0.5*E3*B1^2*E6 + B10*B1*E6 + 2*B4*B1*RAIZ(E6))', None, False),
        ('D8', 'FS = Pp/Pa', None, True),
        ('E8', None, 'SI(E5=0;0;E7/E5)', None, False),
        ('D9', 'Evaluación', None, True),
        ('E9', None, 'SI(E8<1;"CRITICO";SI(E8<1.5;"MARGINAL";"ACEPTABLE"))', None, False),
    ]

    for ref, label, formula, is_label, is_string in result_entries:
        if label is not None and formula is None:
            rows.append(f'    <row r="{ref[1:]}">\n      {value_cell(ref, label)}\n    </row>')
        elif formula is not None:
            if ref == 'E9':
                rows.append(f'    <row r="{ref[1:]}">\n      <c r="{ref}" t="str"><f>SI(E8&lt;1;"CRITICO";SI(E8&lt;1.5;"MARGINAL";"ACEPTABLE"))</f><v>ACEPTABLE</v></c>\n    </row>')
            else:
                rows.append(f'    <row r="{ref[1:]}">\n      <c r="{ref}"><f>{escape(formula)}</f></c>\n    </row>')

    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <dimension ref="A1:E11"/>
  <sheetViews>
    <sheetView workbookViewId="0"/>
  </sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  <cols>
    <col min="1" max="1" width="18"/>
    <col min="2" max="2" width="15"/>
    <col min="3" max="3" width="10"/>
    <col min="4" max="4" width="18"/>
    <col min="5" max="5" width="30"/>
  </cols>
  <sheetData>
%s
  </sheetData>
</worksheet>
''' % ('\n'.join(rows))


def build_sheet2_xml():
    # Summary sheet with Excel-friendly labels and formulas
    rows = [
        '    <row r="1"><c r="A1" t="inlineStr"><is><t>Resultado final</t></is></c></row>',
        '    <row r="3"><c r="A3" t="inlineStr"><is><t>Empuje Activo Pa</t></is></c><c r="B3"><f>E5</f></c></row>',
        '    <row r="4"><c r="A4" t="inlineStr"><is><t>Empuje Pasivo Pp</t></is></c><c r="B4"><f>E7</f></c></row>',
        '    <row r="5"><c r="A5" t="inlineStr"><is><t>Kae</t></is></c><c r="B5"><f>E4</f></c></row>',
        '    <row r="6"><c r="A6" t="inlineStr"><is><t>Kpe</t></is></c><c r="B6"><f>E6</f></c></row>',
        '    <row r="7"><c r="A7" t="inlineStr"><is><t>Θ [°]</t></is></c><c r="B7"><f>E2</f></c></row>',
        '    <row r="8"><c r="A8" t="inlineStr"><is><t>FS</t></is></c><c r="B8"><f>E8</f></c></row>',
        '    <row r="9"><c r="A9" t="inlineStr"><is><t>Evaluación</t></is></c><c r="B9"><f>E9</f></c></row>',
    ]
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <dimension ref="A1:B9"/>
  <sheetViews><sheetView workbookViewId="0"/></sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  <sheetData>
%s
  </sheetData>
</worksheet>
''' % '\n'.join(rows)


def write_xlsx(path):
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>'''

    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''

    workbook = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Datos" sheetId="1" r:id="rId1"/>
    <sheet name="Resultados" sheetId="2" r:id="rId2"/>
  </sheets>
</workbook>'''

    wb_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''

    styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="1"><fill><patternFill patternType="none"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''

    app = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Excel</Application>
</Properties>'''

    core = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                  xmlns:dc="http://purl.org/dc/elements/1.1/"
                  xmlns:dcterms="http://purl.org/dc/terms/"
                  xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:creator>Copilot</dc:creator>
  <cp:lastModifiedBy>Copilot</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-10-06T00:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-10-06T00:00:00Z</dcterms:modified>
</cp:coreProperties>'''

    with ZipFile(path, 'w', ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('docProps/core.xml', core)
        z.writestr('docProps/app.xml', app)
        z.writestr('xl/workbook.xml', workbook)
        z.writestr('xl/_rels/workbook.xml.rels', wb_rels)
        z.writestr('xl/styles.xml', styles)
        z.writestr('xl/worksheets/sheet1.xml', build_sheet1_xml())
        z.writestr('xl/worksheets/sheet2.xml', build_sheet2_xml())

    print(f'Archivo generado: {path}')


if __name__ == '__main__':
    write_xlsx('muro_sismico_plantilla.xlsx')
