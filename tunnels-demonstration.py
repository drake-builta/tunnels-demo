import marimo

__generated_with = "0.20.4"
app = marimo.App(
    width="medium",
    css_file="https://raw.githubusercontent.com/Haleshot/marimo-themes/refs/heads/main/themes/nord/nord.css",
    auto_download=["ipynb"],
)


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
    import marimo as mo
    import pandas as pd
    import altair as alt

    return alt, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fetch NTI Dataset
    """)
    return


@app.cell(hide_code=True)
def _():
    import duckdb as ddb

    df = ddb.sql(f"""
        SELECT 
            tunnels.I1,
            A1,
            A2,
            A4,
            A5,
            L1,
            L2,
            L3,
            L4,
            L5,
            L6,
            L7,
            L8,
            L9,
            EN::VARCHAR AS EN,
            CS1::INTEGER AS CS1,
            CS2::INTEGER AS CS2,
            CS3::INTEGER AS CS3,
            CS4::INTEGER AS CS4,
            TOTALQTY::INTEGER AS TOTALQTY

        FROM 'tunnels.csv'
            INNER JOIN 'elements.csv'
            ON tunnels.I1 = elements.I1;
        """).df()

    df
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Interactive Tool
    """)
    return


@app.cell(hide_code=True)
def _(df, mo):
    # Calculate element condition percentages
    df['PCT_CS1'] = df.CS1 / df.TOTALQTY
    df['PCT_CS2'] = df.CS2 / df.TOTALQTY
    df['PCT_CS3'] = df.CS3 / df.TOTALQTY
    df['PCT_CS4'] = df.CS4 / df.TOTALQTY

    EN_options = df.EN.unique()

    # Create a form with multiple elements.
    # User must submit the form for a plot to be generated.


    elems=mo.ui.multiselect(options=EN_options, label="Elements")
    conds=mo.ui.range_slider(start=1, stop=4, step=1, label="Condition States")
    mo.md(f'''
        **Select a combination of tunnel elements and condition states**

        {elems}

        {conds}
    ''')



    # form = (
    #     mo.md('''
    #     **Select a combination of tunnel elements and condition states**

    #     {elems}

    #     {conds}
    # ''')
    #     .batch(
    #         elems=mo.ui.multiselect(options=EN_options, label="Elements"),
    #         conds=mo.ui.range_slider(start=1, stop=4, step=1, label="Condition States"),
    #     )
    #     .form(show_clear_button=True, bordered=True)
    # )

    # form
    return conds, elems


@app.cell(hide_code=True)
def _(alt, conds, df, elems, mo):
    # mo.stop(form.value is None, mo.md("Submit the form to continue"))

    _df = df

    # if (form.value != None):
    _df = _df[_df.EN.isin(elems.value)].copy()
    fetched_ids = _df.I1

    # Calculate the number of truck cycles experienced
    _df['RECENT_WORK'] = _df[['A1','A2']].max(axis=1).astype(int)
    _df['AGE']  = 2026 - _df.RECENT_WORK.astype(int)
    _df['ADTT'] = _df.A5.astype(int)
    _df['TRUCK_CYCLES'] = _df.ADTT * _df.AGE

    # Aggregate the condition states
    _cols = []
    _cond_range = range(conds.value[0], conds.value[1] + 1)
    for _cond in (_cond_range):
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
def _(elems, fig1, mo):

    # Display the plot

    if (len(elems.value) > 0):
        _fig = fig1
        _tbl = mo.ui.table(_fig.value)
    else:
        _fig = mo.md("Select one or more elements in the dropdown above to view this chart.")
        _tbl = mo.md("")

    print(elems.value)

    mo.vstack([
        mo.md("### Reactive Scatterplot"),
        _fig,
        _tbl
    ])

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
