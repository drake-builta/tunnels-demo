import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium", auto_download=["ipynb"])


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Demonstration Notebook
    *Analyzing the National Tunnel Inventory with Marimo notebooks and altair for deploying a reactive analysis app.*
    ***
    """)
    return


@app.cell
def _():
    import requests
    import io

    import marimo as mo
    import pandas as pd
    import altair as alt
    from pyodide.http import pyxhr

    import configs

    return alt, configs, io, mo, pd, pyxhr, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fetch NTI Dataset
    """)
    return


@app.cell
def _(configs, io, mo, pd, pyxhr, requests):
    try:
        _loc = mo.notebook_location()
        if _loc:
            _response = pyxhr.get(configs.getInventoryDataPath())
            # Code specific to running in a WASM environment (browser-based)
            # mo.md("This notebook is running in WASM!")
    except:
        _response = requests.get(configs.getInventoryDataPath())
        # Code specific to running in a standard environment (with a Python backend)
        # mo.md("This notebook is running with a Python backend.")


    _xml_content = _response.content.replace(b'\x00', b'')

    # Primary dataset (row per tunnel)
    df =     pd.read_xml(io.BytesIO(_xml_content), dtype="object", xpath="//TunnelInstance")

    # Secondary dataset (row per tunnel element)
    df_els = pd.read_xml(io.BytesIO(_xml_content), dtype="object", xpath="//FHWAED")
    return df, df_els


@app.cell
def _(df):
    df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Interactive Tool
    """)
    return


@app.cell(hide_code=True)
def _(df, df_els, pd):
    # Calculate element condition percentages
    for i in list(range(1, 5, 1)):
        i = str(i)
        df_els['PCT_CS'+i] = df_els['CS'+i].astype(int) / df_els.TOTALQTY.astype(int)

    # Prepare and merge the datasets on I1 (the unique identifier for each tunnel)
    _cols = [
        'I1',
        'A1',
        'A2',
        'A4',
        'A5',
        'L1',
        'L2',
        'L3',
        'L4',
        'L5',
        'L6',
        'L7',
        'L8',
        'L9'
    ]

    def getMergedDataFrame():
        df_merged = pd.merge(df_els, df[_cols], how="inner", on="I1")
        return df_merged


    return (getMergedDataFrame,)


@app.cell(hide_code=True)
def _(getMergedDataFrame, mo):
    EN_options = getMergedDataFrame().EN.unique()

    # Create a form with multiple elements.
    # User must submit the form for a plot to be generated.
    form = (
        mo.md('''
        **Select a combination of tunnel elements and condition states**

        {elems}

        {conds}
    ''')
        .batch(
            elems=mo.ui.multiselect(options=EN_options, label="Elements"),
            conds=mo.ui.range_slider(start=1, stop=4, step=1, label="Condition States"),
        )
        .form(show_clear_button=True, bordered=True)
    )

    form
    return (form,)


@app.cell(hide_code=True)
def _(alt, form, getMergedDataFrame, mo):
    _df = getMergedDataFrame()

    if (form.value != None):
        _df = _df[_df.EN.isin(form.value["elems"])].copy()
        fetched_ids = _df.I1
    
        # Calculate the number of truck cycles experienced
        _df['RECENT_WORK'] = _df[['A1','A2']].max(axis=1).astype(int)
        _df['AGE']  = 2026 - _df.RECENT_WORK.astype(int)
        _df['ADTT'] = _df.A5.astype(int)
        _df['TRUCK_CYCLES'] = _df.ADTT * _df.AGE
    
        # Aggregate the condition states
        _cols = []
        for _cond in (form.value["conds"]):
            _cols.append(f"PCT_CS{_cond}")
            _colname = " + ".join(_cols)
            _df[_colname] = _df[_cols].sum(axis=1)
    
        fig1 = mo.ui.altair_chart(alt.Chart(_df).mark_point().encode(
            x='TRUCK_CYCLES',
            y=_colname,
            color='EN'
        ))
    return (fig1,)


@app.cell(hide_code=True)
def _(fig1, form, mo):
    # Display the plot

    if (form.value != None):
        mo.vstack([
            mo.md("### Reactive Scatterplot"),
            mo.md("Tip: *Select one or more data points in the chart to show these records in the table.*"),
            fig1, 
            mo.ui.table(fig1.value)
        ])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
