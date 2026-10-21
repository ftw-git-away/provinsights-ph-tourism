"""Build resources/seeds/map_unit_coordinates.csv: one point per reporting unit (100) for the dashboard map.

Source: OCHA HDX "Philippines - Subnational Administrative Boundaries" (COD-AB, NAMRIA and PSA),
file phl_admin_boundaries.xlsx, sheets phl_admin1/2/3, columns center_lat and center_lon. Licence CC BY-IGO.
Usage: python resources/seeds/tools/build_map_unit_coordinates.py <phl_admin_boundaries.xlsx> <units: 04_gold.dim_province exported as parquet or csv (province_psgc, province_name, unit_type)> <out.csv>
"""
import sys, pandas as pd

XLSX, UNITS, OUT = sys.argv[1:4]
x = pd.ExcelFile(XLSX)
a1, a2, a3 = (x.parse(f"phl_admin{i}") for i in (1, 2, 3))
version = f"COD-AB {a2.version.iloc[0]}, valid on {pd.Timestamp(a2.valid_on.iloc[0]).date()}"
units = pd.read_parquet(UNITS) if UNITS.endswith(("parquet", "/")) or "." not in UNITS.split("/")[-1] else pd.read_csv(UNITS, dtype=str)
units = units[["province_psgc", "province_name", "unit_type"]].copy()

# Units whose COD-AB record cannot be found from the PSGC code: COD-AB keeps HUCs as cities inside their
# parent province (older codes), has no Negros Island Region, and places Sulu in BARMM.
BY_PCODE = {
    "1300000000": ("adm1", "PH13"),          # NCR: region level
    "0330100000": ("adm3", "PH0305401"),     # City of Angeles (inside Pampanga in COD-AB)
    "0331400000": ("adm3", "PH0307107"),     # City of Olongapo (Zambales)
    "0631000000": ("adm3", "PH0603022"),     # City of Iloilo (Iloilo)
    "0730600000": ("adm3", "PH0702217"),     # City of Cebu (Cebu)
    "0731100000": ("adm3", "PH0702226"),     # City of Lapu-Lapu (Cebu)
    "0731300000": ("adm3", "PH0702230"),     # City of Mandaue (Cebu)
    "0831600000": ("adm3", "PH0803747"),     # City of Tacloban (Leyte)
    "0931700000": ("adm3", "PH0907332"),     # City of Zamboanga (Zamboanga del Sur)
    "0990101000": ("adm3", "PH0909701"),     # City of Isabela
    "1030500000": ("adm3", "PH1004305"),     # City of Cagayan de Oro (Misamis Oriental)
    "1030900000": ("adm3", "PH1003504"),     # City of Iligan (Lanao del Norte)
    "1130700000": ("adm3", "PH1102402"),     # City of Davao (Davao del Sur)
    "1230800000": ("adm3", "PH1206303"),     # City of General Santos (South Cotabato)
    "1430300000": ("adm3", "PH1401102"),     # City of Baguio (Benguet)
    "1630400000": ("adm3", "PH1600202"),     # City of Butuan (Agusan del Norte)
    "1731500000": ("adm3", "PH1705316"),     # City of Puerto Princesa (Palawan)
    "1830200000": ("adm3", "PH0604501"),     # City of Bacolod (Negros Occidental in COD-AB)
    "0906600000": ("adm2", "PH19066"),       # Sulu (BARMM in COD-AB; Region IX in PSGC 2Q 2026)
    "1804500000": ("adm2", "PH06045"),       # Negros Occidental (Region VI in COD-AB; NIR in PSGC)
    "1804600000": ("adm2", "PH07046"),       # Negros Oriental (Region VII in COD-AB; NIR in PSGC)
    "1806100000": ("adm2", "PH07061"),       # Siquijor (Region VII in COD-AB; NIR in PSGC)
}
# COD-AB's point for Palawan lies on Busuanga in the northern islands, about 280 km from the province's area-weighted
# centre. Use the municipality nearest that centre (Puerto Princesa and Kalayaan excluded): Aborlan.
OVERRIDES = {"1705300000": ("adm3", "PH1705301",
             "Province point moved to Aborlan: COD-AB's point for Palawan falls on Busuanga, far from the mainland.")}

tables = {"adm1": a1.rename(columns={"adm1_pcode": "pcode", "adm1_name": "name"}),
          "adm2": a2.rename(columns={"adm2_pcode": "pcode", "adm2_name": "name"}),
          "adm3": a3.rename(columns={"adm3_pcode": "pcode", "adm3_name": "name"})}
lookup = {lvl: t.set_index("pcode")[["name", "center_lat", "center_lon"]] for lvl, t in tables.items()}

rows = []
for u in units.itertuples():
    override_note = None
    if u.province_psgc in OVERRIDES:
        level, pcode, override_note = OVERRIDES[u.province_psgc]
        method = "override"
    elif u.province_psgc in BY_PCODE:
        level, pcode = BY_PCODE[u.province_psgc]
        method = "listed"
    else:
        level, pcode = "adm2", "PH" + u.province_psgc[:5]
        method = "psgc_code"
    rec = lookup[level].loc[pcode]
    note = {"adm1": "Region centre (NCR is one unit).",
            "adm3": "City centre; COD-AB keeps this city inside its parent province.",
            "adm2": "Province centre; COD-AB province area includes any HUC inside it."}[level]
    note = override_note or note
    rows.append({"province_psgc": u.province_psgc, "province_name": u.province_name, "unit_type": u.unit_type,
                 "latitude": round(float(rec.center_lat), 6), "longitude": round(float(rec.center_lon), 6),
                 "codab_pcode": pcode, "codab_name": rec["name"], "codab_level": level,
                 "match_method": method, "note": note, "source_version": version,
                 "reviewed_by": None, "reviewed_on": None})
out = pd.DataFrame(rows).sort_values("province_psgc")
assert len(out) == 100 and out.province_psgc.is_unique
assert out.latitude.between(4.4, 21.2).all() and out.longitude.between(116.0, 127.0).all()
out.to_csv(OUT, index=False)
print(f"{len(out)} rows -> {OUT} ({version}); methods: {out.match_method.value_counts().to_dict()}")
